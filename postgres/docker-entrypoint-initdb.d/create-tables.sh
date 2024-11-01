-!/bin/ash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- Request ----------------------------------------------------------------

    CREATE TABLE IF NOT EXISTS public.request
    (
        request_time timestamp with time zone NOT NULL,
        status_code integer NOT NULL,
        request_duration integer NOT NULL,
        method text COLLATE pg_catalog."default" NOT NULL,
        response_size integer NOT NULL,
        uri text COLLATE pg_catalog."default" NOT NULL,
        user_agent text COLLATE pg_catalog."default" NOT NULL,
        CONSTRAINT request_pkey PRIMARY KEY (request_time, uri, method, status_code, request_duration, response_size, user_agent)
    )

    TABLESPACE pg_default;

    ALTER TABLE public.request
        OWNER to $POSTGRES_USER;
EOSQL
