-- Stored Procedures für die E-Mobility-Webanwendung
-- PostgreSQL-kompatibel · wird bei Applikationsstart automatisch angelegt
-- (siehe app/__init__.py → _create_stored_procedures)

-- ──────────────────────────────────────────────────────────────────────────────
-- sp_start_rental
--   Startet eine Ausleihe nach Prüfung von Fahrzeugverfügbarkeit und QR-Code.
--   Gibt die neue rental_id zurück oder wirft eine Exception.
-- ──────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION sp_start_rental(
    p_vehicle_id  INTEGER,
    p_rider_id    INTEGER,
    p_unlock_code VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    v_rental_id        INTEGER;
    v_vehicle_status   VARCHAR;
    v_vehicle_code     VARCHAR;
    v_vehicle_lat      NUMERIC(9,6);
    v_vehicle_lon      NUMERIC(9,6);
    v_payment_method   VARCHAR;
BEGIN
    -- Zahlungsmittel prüfen
    SELECT payment_method INTO v_payment_method
    FROM users WHERE id = p_rider_id;
    IF v_payment_method IS NULL OR v_payment_method = '' THEN
        RAISE EXCEPTION 'Bitte zuerst ein Zahlungsmittel hinterlegen.';
    END IF;

    -- Fahrzeugdaten laden
    SELECT status, unlock_code, latitude, longitude
    INTO v_vehicle_status, v_vehicle_code, v_vehicle_lat, v_vehicle_lon
    FROM vehicles WHERE id = p_vehicle_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Fahrzeug nicht gefunden.';
    END IF;

    IF v_vehicle_status <> 'available' THEN
        RAISE EXCEPTION 'Fahrzeug ist derzeit nicht verfügbar.';
    END IF;

    IF p_unlock_code IS NULL OR TRIM(p_unlock_code) <> v_vehicle_code THEN
        RAISE EXCEPTION 'Ungültiger Entriegelungscode (QR-Code). Bitte den Code am Fahrzeug scannen.';
    END IF;

    -- Aktive Ausleihe prüfen
    IF EXISTS (
        SELECT 1 FROM rentals
        WHERE rider_id = p_rider_id AND status = 'active'
    ) THEN
        RAISE EXCEPTION 'Es existiert bereits eine aktive Ausleihe.';
    END IF;

    -- Fahrzeugstatus auf "rented" setzen
    UPDATE vehicles SET status = 'rented' WHERE id = p_vehicle_id;

    -- Neue Ausleihe anlegen
    INSERT INTO rentals (
        vehicle_id, rider_id, start_km,
        start_latitude, start_longitude
    ) VALUES (
        p_vehicle_id, p_rider_id, 0,
        v_vehicle_lat, v_vehicle_lon
    ) RETURNING id INTO v_rental_id;

    RETURN v_rental_id;
END;
$$ LANGUAGE plpgsql;


-- ──────────────────────────────────────────────────────────────────────────────
-- sp_end_rental
--   Beendet eine aktive Ausleihe, berechnet Gesamtpreis und senkt den
--   Akkustand des Fahrzeugs um 2 % pro gefahrenen km.
-- ──────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION sp_end_rental(
    p_rental_id  INTEGER,
    p_end_km     NUMERIC,
    p_latitude   NUMERIC,
    p_longitude  NUMERIC
) RETURNS VOID AS $$
DECLARE
    v_rental          RECORD;
    v_distance        NUMERIC;
    v_battery_drain   INTEGER;
    v_new_battery     INTEGER;
    v_duration_min    INTEGER;
    v_total_price     NUMERIC;
BEGIN
    SELECT * INTO v_rental FROM rentals WHERE id = p_rental_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Ausleihe nicht gefunden.';
    END IF;

    IF v_rental.status <> 'active' THEN
        RAISE EXCEPTION 'Ausleihe ist bereits beendet.';
    END IF;

    IF p_end_km < v_rental.start_km THEN
        RAISE EXCEPTION 'Der Endkilometerstand darf nicht kleiner als der Startkilometerstand sein.';
    END IF;

    IF p_latitude NOT BETWEEN -90 AND 90 THEN
        RAISE EXCEPTION 'Ungültiger Breitengrad.';
    END IF;

    IF p_longitude NOT BETWEEN -180 AND 180 THEN
        RAISE EXCEPTION 'Ungültiger Längengrad.';
    END IF;

    -- Berechnungen
    v_distance      := GREATEST(0, p_end_km - v_rental.start_km);
    v_battery_drain := LEAST(
                           ROUND(v_distance * 2)::INTEGER,
                           (SELECT battery_level FROM vehicles WHERE id = v_rental.vehicle_id)
                       );
    v_duration_min  := GREATEST(
                           1,
                           EXTRACT(EPOCH FROM (NOW() - v_rental.start_time)) / 60
                       )::INTEGER;
    v_total_price   := v_rental.base_price + (v_rental.price_per_minute * v_duration_min);

    -- Ausleihe abschliessen
    UPDATE rentals SET
        end_time    = NOW(),
        end_km      = p_end_km,
        end_latitude  = p_latitude,
        end_longitude = p_longitude,
        status      = 'completed',
        total_price = ROUND(v_total_price, 2),
        distance_km = ROUND(v_distance, 2)
    WHERE id = p_rental_id;

    -- Fahrzeug aktualisieren: Position, Status und Akkustand
    SELECT battery_level INTO v_new_battery
    FROM vehicles WHERE id = v_rental.vehicle_id;

    v_new_battery := GREATEST(0, v_new_battery - v_battery_drain);

    UPDATE vehicles SET
        latitude      = p_latitude,
        longitude     = p_longitude,
        status        = 'available',
        battery_level = v_new_battery
    WHERE id = v_rental.vehicle_id;
END;
$$ LANGUAGE plpgsql;
