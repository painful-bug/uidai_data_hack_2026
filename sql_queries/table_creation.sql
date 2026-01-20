CREATE OR ALTER PROCEDURE dbo.create_api_aadhar_tables AS
BEGIN
    DECLARE @start_time DATETIME, @end_time DATETIME;

    BEGIN TRY
        PRINT '-------------------------------------';
        PRINT 'Starting API Aadhar Table Creation';
        PRINT '-------------------------------------';

        SET @start_time = GETDATE();

        -----------------------------
        -- api_data_aadhar_biometric
        -----------------------------
        IF OBJECT_ID('api_data_aadhar_biometric', 'U') IS NOT NULL
        BEGIN
            PRINT '>> Dropping Existing Table: api_data_aadhar_biometric';
            DROP TABLE api_data_aadhar_biometric;
        END

        CREATE TABLE api_data_aadhar_biometric (
            date_of_data DATE,
            state_name NVARCHAR(100),
            district_name NVARCHAR(100),
            pincode INT,
            bio_age_5_17 INT,
            bio_age_17_ INT
        );

        -----------------------------
        -- api_data_aadhar_demographic
        -----------------------------
        IF OBJECT_ID('api_data_aadhar_demographic', 'U') IS NOT NULL
        BEGIN
            PRINT '>> Dropping Existing Table: api_data_aadhar_demographic';
            DROP TABLE api_data_aadhar_demographic;
        END

        CREATE TABLE api_data_aadhar_demographic (
            date_of_data DATE,
            state_name NVARCHAR(100),
            district_name NVARCHAR(100),
            pincode INT,
            demo_age_5_17 INT,
            demo_age_17_ INT
        );

        -----------------------------
        -- api_data_aadhar_enrollment
        -----------------------------
        IF OBJECT_ID('api_data_aadhar_enrollment', 'U') IS NOT NULL
        BEGIN
            PRINT '>> Dropping Existing Table: api_data_aadhar_enrollment';
            DROP TABLE api_data_aadhar_enrollment;
        END

        CREATE TABLE api_data_aadhar_enrollment (
            date_of_data DATE,
            state_name NVARCHAR(100),
            district_name NVARCHAR(100),
            pincode INT,
            age_0_5 INT,
            age_5_17 INT,
            age_18_greater INT
        );

        SET @end_time = GETDATE();

        PRINT '-------------------------------------';
        PRINT 'API Aadhar Table Creation Completed Successfully';
        PRINT 'Start Time: ' + CAST(@start_time AS NVARCHAR(30)) + ' | End Time: ' + CAST(@end_time AS NVARCHAR(30));
        PRINT 'Total Duration: ' + CAST(DATEDIFF(SECOND, @start_time, @end_time) AS NVARCHAR(10)) + ' Seconds';
        PRINT '-------------------------------------';

    END TRY
    BEGIN CATCH
        PRINT 'Error Occurred During API Aadhar Table Creation: ' 
            + ' Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR(10)) 
            + ' Message: ' + ERROR_MESSAGE() 
            + ' At Line: ' + CAST(ERROR_LINE() AS NVARCHAR(10));
    END CATCH
END;
GO

EXEC dbo.create_api_aadhar_tables;
