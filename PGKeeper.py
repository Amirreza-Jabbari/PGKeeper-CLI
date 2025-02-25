import os
import subprocess
import logging
import click
from datetime import datetime

# -------------------------
# Logging Configuration
# -------------------------
# The CLI accepts options for log level and log file.
@click.group()
@click.option('--log-level', default='INFO', show_default=True,
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).')
@click.option('--log-file', default='./backup_manager.log', show_default=True,
              help='Path to the log file; logs will also be written to this file.')
@click.pass_context
def cli(ctx, log_level, log_file):
    """
    CLI tool for PostgreSQL database backup and restore.
    
    This tool uses pg_dump and pg_restore (or psql for plain text dumps)
    via subprocess to perform backup and restore operations.
    """
    # Set up logging handlers: console and file (if provided)
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise click.BadParameter(f"Invalid log level: {log_level}")
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    logging.info("Starting PGKeeper for PostgreSQL backup and restore")
    ctx.obj = {}

# -------------------------
# Backup Command
# -------------------------
@cli.command()
@click.option('--host', required=True, help="PostgreSQL server host (e.g., localhost)")
@click.option('--port', default=5432, type=int, show_default=True, help="PostgreSQL server port")
@click.option('--username', required=True, help="Database username")
@click.option('--dbname', required=True, help="Name of the database to backup")
@click.option('--backup-dir', default="./backups", show_default=True, help="Directory to store backup files")
@click.option('--format', 'dump_format', default='c', show_default=True,
              type=click.Choice(['c', 'd', 't', 'p']),
              help="Dump format: c (custom), d (directory), t (tar), p (plain)")
@click.option('--password', prompt=True, hide_input=True, help="Database password")
def backup(host, port, username, dbname, backup_dir, dump_format, password):
    """
    Backup the PostgreSQL database using pg_dump.

    This command connects to the specified database and uses pg_dump to create a backup.
    The backup file (or directory, if dump format is 'd') is created in a timestamped
    subdirectory under the specified backup directory.
    """
    # Create a timestamped backup path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if dump_format == 'd':
        backup_path = os.path.join(backup_dir, f"backup_{dbname}_{timestamp}")
    else:
        # Choose file extension based on dump format
        file_ext = ".dump" if dump_format == 'c' else ".tar" if dump_format == 't' else ".sql"
        backup_path = os.path.join(backup_dir, f"backup_{dbname}_{timestamp}{file_ext}")
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        logging.info(f"Backup directory ensured: {backup_dir}")
    except Exception as e:
        logging.error(f"Failed to create backup directory: {e}")
        return

    # Set the environment variable for PGPASSWORD
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    # Build the pg_dump command
    if dump_format == 'd':
        cmd = [
            "pg_dump",
            "-h", host,
            "-p", str(port),
            "-U", username,
            "-F", dump_format,
            "-v",
            "-f", backup_path,
            dbname
        ]
    else:
        cmd = [
            "pg_dump",
            "-h", host,
            "-p", str(port),
            "-U", username,
            "-F", dump_format,
            "-b",  # include large objects
            "-v",
            "-f", backup_path,
            dbname
        ]
    
    logging.debug("Running command: " + " ".join(cmd))
    try:
        subprocess.run(cmd, env=env, check=True)
        logging.info(f"Backup completed successfully. Backup file/directory: {backup_path}")
        click.echo(f"Backup completed successfully. Backup file/directory: {backup_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Backup failed: {e}")
        click.echo(f"Backup failed: {e}")

# -------------------------
# Restore Command
# -------------------------
@cli.command()
@click.option('--host', required=True, help="PostgreSQL server host (e.g., localhost)")
@click.option('--port', default=5432, type=int, show_default=True, help="PostgreSQL server port")
@click.option('--username', required=True, help="Database username")
@click.option('--dbname', required=True, help="Name of the database to restore to")
@click.option('--backup-file', required=True, help="Path to the backup file or directory (if directory format, use that directory)")
@click.option('--password', prompt=True, hide_input=True, help="Database password")
def restore(host, port, username, dbname, backup_file, password):
    """
    Restore the PostgreSQL database from backup.

    This command restores the database using pg_restore (or psql if the backup is in plain text format).
    It uses the backup file (or directory, if the dump format was directory) to restore the data.
    """
    # Set the environment variable for PGPASSWORD
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    # Determine if backup_file is a directory (for directory format) or a file.
    if os.path.isdir(backup_file):
        # Directory format: use pg_restore
        cmd = [
            "pg_restore",
            "-h", host,
            "-p", str(port),
            "-U", username,
            "-d", dbname,
            "-v",
            backup_file
        ]
    else:
        # For file formats: if plain text (.sql), use psql; else use pg_restore
        if backup_file.endswith(".sql"):
            cmd = [
                "psql",
                "-h", host,
                "-p", str(port),
                "-U", username,
                "-d", dbname,
                "-f", backup_file
            ]
        else:
            cmd = [
                "pg_restore",
                "-h", host,
                "-p", str(port),
                "-U", username,
                "-d", dbname,
                "-v",
                backup_file
            ]
    
    logging.debug("Running command: " + " ".join(cmd))
    try:
        subprocess.run(cmd, env=env, check=True)
        logging.info("Restore completed successfully.")
        click.echo("Restore completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Restore failed: {e}")
        click.echo(f"Restore failed: {e}")

if __name__ == '__main__':
    cli()
