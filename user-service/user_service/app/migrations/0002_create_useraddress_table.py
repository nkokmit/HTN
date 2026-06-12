from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS app_useraddress (
                    id bigserial PRIMARY KEY,
                    full_name varchar(255) NOT NULL,
                    phone_number varchar(20) NOT NULL,
                    city varchar(100) NOT NULL,
                    district varchar(100) NOT NULL,
                    ward varchar(100) NOT NULL,
                    detail_address varchar(255) NOT NULL,
                    is_default boolean NOT NULL DEFAULT false,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    user_id bigint NOT NULL REFERENCES app_useraccount(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS app_useraddress_user_id_9f3b0f1d ON app_useraddress (user_id);
                CREATE INDEX IF NOT EXISTS app_useraddress_is_default_0b0dd7f6 ON app_useraddress (is_default);
            """,
            reverse_sql="DROP TABLE IF EXISTS app_useraddress CASCADE;",
        ),
    ]