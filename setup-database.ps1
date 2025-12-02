# Connect to PostgreSQL and create the table

# Using psql (if installed)
$env:PGPASSWORD="e694313dfb09a85a0f5"
psql -h postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com -p 6974 -U 30b40be4db3f -d XMCMDsOblizg -f create-products-table.sql

# Or using Docker with postgres client
docker run --rm -it postgres:15 psql "postgresql://30b40be4db3f:e694313dfb09a85a0f5@postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com:6974/XMCMDsOblizg?sslmode=require" -f /path/to/create-products-table.sql
