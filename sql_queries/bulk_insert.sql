CREATE OR ALTER PROCEDURE dbo.bulk_insert_api_aadhar_data
    @data_path NVARCHAR(500) = '/Users/aishik/Desktop/uidai_data_hack_2026/datasets/'
-- Update this path to where CSV files are located on the SQL Server
AS
BEGIN
    DECLARE @start_time DATETIME, @end_time DATETIME;
    DECLARE @sql NVARCHAR(MAX);
    DECLARE @biometric_path NVARCHAR(500);
    DECLARE @demographic_path NVARCHAR(500);
    DECLARE @enrollment_path NVARCHAR(500);

    BEGIN TRY
        PRINT '-------------------------------------';
        PRINT 'Starting Bulk Insert for API Aadhar Data';
        PRINT '-------------------------------------';

        SET @start_time = GETDATE();

        -- Build full file paths
        SET @biometric_path = @data_path + 'api_data_aadhar_biometric_combined.csv';
        SET @demographic_path = @data_path + 'api_data_aadhar_demographic_combined.csv';
        SET @enrollment_path = @data_path + 'api_data_aadhar_enrolment_combined.csv';

        -----------------------------
        -- Bulk Insert: api_data_aadhar_biometric
        -----------------------------
        PRINT '>> Truncating Table: api_data_aadhar_biometric';
        TRUNCATE TABLE api_data_aadhar_biometric;

        PRINT '>> Bulk Inserting: api_data_aadhar_biometric_combined.csv';
        SET @sql = '
        BULK INSERT api_data_aadhar_biometric
        FROM ''' + @biometric_path + '''
        WITH (
            FORMAT = ''CSV'',
            FIRSTROW = 2,
            FIELDTERMINATOR = '','',
            ROWTERMINATOR = ''\n'',
            TABLOCK,
            MAXERRORS = 0
        );';
        EXEC sp_executesql @sql;
        PRINT '>> Bulk Insert Completed: api_data_aadhar_biometric';

        -----------------------------
        -- Bulk Insert: api_data_aadhar_demographic
        -----------------------------
        PRINT '>> Truncating Table: api_data_aadhar_demographic';
        TRUNCATE TABLE api_data_aadhar_demographic;

        PRINT '>> Bulk Inserting: api_data_aadhar_demographic_combined.csv';
        SET @sql = '
        BULK INSERT api_data_aadhar_demographic
        FROM ''' + @demographic_path + '''
        WITH (
            FORMAT = ''CSV'',
            FIRSTROW = 2,
            FIELDTERMINATOR = '','',
            ROWTERMINATOR = ''\n'',
            TABLOCK,
            MAXERRORS = 0
        );';
        EXEC sp_executesql @sql;
        PRINT '>> Bulk Insert Completed: api_data_aadhar_demographic';

        -----------------------------
        -- Bulk Insert: api_data_aadhar_enrollment
        -----------------------------
        PRINT '>> Truncating Table: api_data_aadhar_enrollment';
        TRUNCATE TABLE api_data_aadhar_enrollment;

        PRINT '>> Bulk Inserting: api_data_aadhar_enrolment_combined.csv';
        SET @sql = '
        BULK INSERT api_data_aadhar_enrollment
        FROM ''' + @enrollment_path + '''
        WITH (
            FORMAT = ''CSV'',
            FIRSTROW = 2,
            FIELDTERMINATOR = '','',
            ROWTERMINATOR = ''\n'',
            TABLOCK,
            MAXERRORS = 0
        );';
        EXEC sp_executesql @sql;
        PRINT '>> Bulk Insert Completed: api_data_aadhar_enrollment';

        SET @end_time = GETDATE();

        -----------------------------
        -- Summary
        -----------------------------
        PRINT '-------------------------------------';
        PRINT 'Bulk Insert Summary:';
        PRINT '-------------------------------------';
        
                    SELECT 'api_data_aadhar_biometric' AS TableName, COUNT(*) AS [RowCount]
        FROM api_data_aadhar_biometric
    UNION ALL
        SELECT 'api_data_aadhar_demographic', COUNT(*)
        FROM api_data_aadhar_demographic
    UNION ALL
        SELECT 'api_data_aadhar_enrollment', COUNT(*)
        FROM api_data_aadhar_enrollment;

        PRINT '-------------------------------------';
        PRINT 'Bulk Insert Completed Successfully';
        PRINT 'Start Time: ' + CAST(@start_time AS NVARCHAR(30)) + ' | End Time: ' + CAST(@end_time AS NVARCHAR(30));
        PRINT 'Total Duration: ' + CAST(DATEDIFF(SECOND, @start_time, @end_time) AS NVARCHAR(10)) + ' Seconds';
        PRINT '-------------------------------------';

    END TRY
    BEGIN CATCH
        PRINT 'Error Occurred During Bulk Insert: ' 
            + ' Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR(10)) 
            + ' Message: ' + ERROR_MESSAGE() 
            + ' At Line: ' + CAST(ERROR_LINE() AS NVARCHAR(10));
    END CATCH
END;
GO

-- Execute the procedure with the path to your CSV files
-- Update the path parameter to match where your CSV files are located on the SQL Server
EXEC dbo.bulk_insert_api_aadhar_data @data_path = 'C:\datasets\';
