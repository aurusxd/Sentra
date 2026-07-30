# Резервное копирование Sentra

Скрипт `scripts/backup_databases.sh` создаёт согласованный снимок:

- PostgreSQL в custom-формате `pg_dump`;
- каталога Chroma с SQLite и HNSW-индексами;
- volume с исходными загруженными файлами.

Backend останавливается только на время локального снимка. Перед проверкой
архивов и загрузкой на Яндекс Диск он запускается обратно. Если создание
снимка прервётся, обработчик завершения также попытается запустить backend.

## Настройка rclone и Яндекс Диска

Установите `rclone` на сервер и создайте основной remote:

```bash
rclone config
```

Создайте remote с именем `yandex`, выберите тип `Yandex Disk` и завершите
OAuth-авторизацию. Проверьте подключение:

```bash
rclone lsd yandex:
```

Для файлов больше примерно 5 ГиБ Яндекс Диск может долго подтверждать загрузку,
поэтому в примере задан `RCLONE_TIMEOUT=60m`.

Дампы содержат данные пользователей, поэтому поверх Яндекс Диска рекомендуется
создать remote типа `crypt`. Скрипт намеренно отклоняет незашифрованный remote:

```bash
rclone config
```

Для него укажите:

```text
name: yandex-crypt
type: crypt
remote: yandex:Sentra/backups
filename_encryption: standard
directory_name_encryption: true
```

Пароли, созданные для `crypt`, необходимо хранить отдельно от сервера. Без них
восстановить зашифрованные резервные копии невозможно.

Конфигурация должна быть доступна пользователю systemd-сервиса:

```bash
install -d -o root -g docker -m 750 /etc/rclone
install -o root -g docker -m 640 ~/.config/rclone/rclone.conf /etc/rclone/rclone.conf
rclone --config /etc/rclone/rclone.conf lsd yandex-crypt:
```

## Установка systemd timer

Пример предполагает, что проект находится в `/opt/sentra`.

```bash
groupadd --system sentra-backup 2>/dev/null || true
useradd --system --gid sentra-backup --groups docker --home-dir /nonexistent \
  --shell /usr/sbin/nologin sentra-backup 2>/dev/null || true

install -d -o sentra-backup -g docker -m 750 /var/backups/sentra
install -d -o root -g root -m 755 /etc/sentra
install -o root -g root -m 600 scripts/backup.env.example /etc/sentra/backup.env
# Docker Compose читает переменные проекта из .env от имени sentra-backup.
chown root:docker /opt/sentra/.env
chmod 640 /opt/sentra/.env

install -o root -g root -m 644 deploy/systemd/sentra-backup.service \
  /etc/systemd/system/sentra-backup.service
install -o root -g root -m 644 deploy/systemd/sentra-backup.timer \
  /etc/systemd/system/sentra-backup.timer

systemctl daemon-reload
systemctl enable --now sentra-backup.timer
```

Отредактируйте `/etc/sentra/backup.env`, если путь к проекту или имена remote
отличаются. `RCLONE_REMOTE` должен указывать на отдельный каталог: скрипт
автоматически удаляет из него только каталоги с именами временных меток старше
`REMOTE_RETENTION_DAYS`.

Первый запуск выполните вручную:

```bash
systemctl start sentra-backup.service
journalctl -u sentra-backup.service -n 200 --no-pager
systemctl list-timers sentra-backup.timer
```

Проверка содержимого на Яндекс Диске:

```bash
rclone --config /etc/rclone/rclone.conf lsf yandex-crypt:sentra
```

## Формат резервной копии

Каждый снимок хранится в отдельном UTC-каталоге:

```text
2026-07-30T12-00-00Z/
├── MANIFEST.env
├── SHA256SUMS
├── postgres.dump
├── postgres.restore-list
├── chroma.tar.gz
└── uploads.tar.gz
```

После загрузки выполняется `rclone cryptcheck`. Локальные и удалённые снимки
удаляются независимо согласно своим retention-периодам. Значение `0` отключает
соответствующую ротацию.

## Проверка и восстановление

Сначала скачайте конкретный снимок и проверьте контрольные суммы:

```bash
mkdir -p /var/backups/sentra-restore
rclone --config /etc/rclone/rclone.conf copy \
  yandex-crypt:sentra/2026-07-30T12-00-00Z \
  /var/backups/sentra-restore
cd /var/backups/sentra-restore
sha256sum --check SHA256SUMS
pg_restore --list postgres.dump >/dev/null
tar -tzf chroma.tar.gz >/dev/null
tar -tzf uploads.tar.gz >/dev/null
```

Полное восстановление является разрушающей операцией. Перед ним остановите
backend, восстановите PostgreSQL через `pg_restore --clean --if-exists`, затем
замените содержимое volumes `chroma_data` и `uploads_data` соответствующими
архивами. После восстановления запустите backend и проверьте поиск по базе
знаний. Не реже раза в месяц выполняйте тестовое восстановление на отдельном
сервере или в отдельном Compose project.

Для PostgreSQL с требованием RPO меньше часа дополнительно требуется
непрерывное архивирование WAL или резервное копирование средствами управляемого
сервиса. Часовой `pg_dump` не даёт point-in-time recovery.
