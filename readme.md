# PGKeeper - PostgreSQL Backup and Restore CLI

PGKeeper is a command-line tool for managing PostgreSQL database backups and restores. It leverages `pg_dump` and `pg_restore` (or `psql` for plain text dumps) to provide seamless backup and restoration functionality.

## Features
- **Backup PostgreSQL databases** using various dump formats (`custom`, `directory`, `tar`, `plain`)
- **Restore backups** from both file-based and directory-based dumps
- **Logging support** with configurable log levels and log file storage
- **User-friendly CLI** with secure password handling

## Installation
Ensure you have the following dependencies installed:

- Python 3.x
- PostgreSQL utilities (`pg_dump`, `pg_restore`, `psql`)
- `click` package for CLI support

### Install dependencies
```bash
pip install click
```

### Clone the repository
```bash
git clone https://github.com/Amirreza-Jabbari/PGKeeper.git
cd PGKeeper
```

## Usage

### General Command Structure
```bash
python pgkeeper.py [OPTIONS] COMMAND [ARGS]...
```

### Available Commands
- `backup` – Create a backup of a PostgreSQL database
- `restore` – Restore a database from a backup

### Logging Options
You can configure the log level and log file path:
```bash
python pgkeeper.py --log-level INFO --log-file pgkeeper.log
```

## Backup a PostgreSQL Database
```bash
python pgkeeper.py backup \
  --host localhost \
  --port 5432 \
  --username your_user \
  --dbname your_database \
  --backup-dir ./backups \ (optional)
  --format c \ (optional)
  --password your_password \ (optional)
  --log-level DEBUG \ (optional)
  --log-file pgkeeper.log \ (optional/not recommended))
```

- `--host`: PostgreSQL server host.
- `--port`: PostgreSQL server port.
- `--username`: PostgreSQL username.
- `--dbname`: PostgreSQL database name.
- `--backup-dir`: Directory to store backups.
- `--password`: PostgreSQL password. you can use `--password` or let PGKeeper ask for it for safer usage (recommended).
- `--format`: Choose between `c` (custom), `d` (directory), `t` (tar), and `p` (plain SQL). default is `c`.
- `log-level`: Choose between `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. Default is `INFO`.
- The backup is stored in the `./backups` directory with a timestamped filename.

## Example
```bash
python pgkeeper.py backup --host localhost --port 5432 --username postgres --dbname db_name
```

## Restore a PostgreSQL Database
```bash
python pgkeeper.py restore \
  --host localhost \
  --port 5432 \
  --username your_user \
  --dbname your_database \
  --backup-file ./backups/backup_your_database_YYYYMMDD_HHMMSS.dump \
  --password your_password \ (optional/not recommended)
```

- `--backup-file`: Path to the backup file.
- If restoring from a `.sql` file, `psql` is used instead of `pg_restore`.

## Example
```bash
python pgkeeper.py restore --host localhost --port 5432 --username postgres --dbname db_name --backup-file ./backups/backup_your_database_YYYYMMDD_HHMMSS.dump
```

## Error Handling and Logging
Logs are stored in the specified log file (default: `backup_manager.log`). Log levels include:
- `DEBUG` – Detailed debugging information
- `INFO` – General operational messages
- `WARNING` – Indications of potential issues
- `ERROR` – Errors that occurred during operation
- `CRITICAL` – Severe errors requiring immediate attention

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'feat: Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a Pull Request

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
