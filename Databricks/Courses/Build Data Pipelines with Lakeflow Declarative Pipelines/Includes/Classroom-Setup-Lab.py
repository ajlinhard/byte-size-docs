# Databricks notebook source
# MAGIC %run ./Classroom-Setup-Common

# COMMAND ----------


def create_country_lookup_table(in_catalog: str, in_schema: str):
    # List of country abbreviations and names
    country_data = [
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('DZ', 'Algeria'),
        ('AS', 'American Samoa'),
        ('AD', 'Andorra'),
        ('AO', 'Angola'),
        ('AI', 'Anguilla'),
        ('AQ', 'Antarctica'),
        ('AR', 'Argentina'),
        ('AM', 'Armenia'),
        ('AW', 'Aruba'),
        ('AU', 'Australia'),
        ('AT', 'Austria'),
        ('AZ', 'Azerbaijan'),
        ('BS', 'Bahamas'),
        ('BH', 'Bahrain'),
        ('BD', 'Bangladesh'),
        ('BB', 'Barbados'),
        ('BY', 'Belarus'),
        ('BE', 'Belgium'),
        ('BZ', 'Belize'),
        ('BJ', 'Benin'),
        ('BM', 'Bermuda'),
        ('BT', 'Bhutan'),
        ('BO', 'Bolivia'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BW', 'Botswana'),
        ('BR', 'Brazil'),
        ('BN', 'Brunei Darussalam'),
        ('BG', 'Bulgaria'),
        ('BF', 'Burkina Faso'),
        ('BI', 'Burundi'),
        ('KH', 'Cambodia'),
        ('CM', 'Cameroon'),
        ('CA', 'Canada'),
        ('CV', 'Cape Verde'),
        ('KY', 'Cayman Islands'),
        ('CF', 'Central African Republic'),
        ('TD', 'Chad'),
        ('CL', 'Chile'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('KM', 'Comoros'),
        ('CG', 'Congo'),
        ('CD', 'Democratic Republic of the Congo'),
        ('CK', 'Cook Islands'),
        ('CR', 'Costa Rica'),
        ('CI', 'Côte d\'Ivoire'),
        ('HR', 'Croatia'),
        ('CU', 'Cuba'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('DJ', 'Djibouti'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('EC', 'Ecuador'),
        ('EG', 'Egypt'),
        ('SV', 'El Salvador'),
        ('GQ', 'Equatorial Guinea'),
        ('ER', 'Eritrea'),
        ('EE', 'Estonia'),
        ('ET', 'Ethiopia'),
        ('FK', 'Falkland Islands'),
        ('FO', 'Faroe Islands'),
        ('FJ', 'Fiji'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('GA', 'Gabon'),
        ('GM', 'Gambia'),
        ('GE', 'Georgia'),
        ('DE', 'Germany'),
        ('GH', 'Ghana'),
        ('GI', 'Gibraltar'),
        ('GR', 'Greece'),
        ('GL', 'Greenland'),
        ('GD', 'Grenada'),
        ('GP', 'Guadeloupe'),
        ('GU', 'Guam'),
        ('GT', 'Guatemala'),
        ('GN', 'Guinea'),
        ('GW', 'Guinea-Bissau'),
        ('GY', 'Guyana'),
        ('HT', 'Haiti'),
        ('HM', 'Heard Island and McDonald Islands'),
        ('HN', 'Honduras'),
        ('HK', 'Hong Kong'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IN', 'India'),
        ('ID', 'Indonesia'),
        ('IR', 'Iran'),
        ('IQ', 'Iraq'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IT', 'Italy'),
        ('JM', 'Jamaica'),
        ('JP', 'Japan'),
        ('JO', 'Jordan'),
        ('KZ', 'Kazakhstan'),
        ('KE', 'Kenya'),
        ('KI', 'Kiribati'),
        ('KP', 'North Korea'),
        ('KR', 'South Korea'),
        ('KW', 'Kuwait'),
        ('KG', 'Kyrgyzstan'),
        ('LA', 'Laos'),
        ('LV', 'Latvia'),
        ('LB', 'Lebanon'),
        ('LS', 'Lesotho'),
        ('LR', 'Liberia'),
        ('LY', 'Libya'),
        ('LI', 'Liechtenstein'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MO', 'Macao'),
        ('MK', 'North Macedonia'),
        ('MG', 'Madagascar'),
        ('MW', 'Malawi'),
        ('MY', 'Malaysia'),
        ('MV', 'Maldives'),
        ('ML', 'Mali'),
        ('MT', 'Malta'),
        ('MH', 'Marshall Islands'),
        ('MQ', 'Martinique'),
        ('MR', 'Mauritania'),
        ('MU', 'Mauritius'),
        ('YT', 'Mayotte'),
        ('MX', 'Mexico'),
        ('FM', 'Federated States of Micronesia'),
        ('MD', 'Moldova'),
        ('MC', 'Monaco'),
        ('MN', 'Mongolia'),
        ('ME', 'Montenegro'),
        ('MS', 'Montserrat'),
        ('MA', 'Morocco'),
        ('MZ', 'Mozambique'),
        ('MM', 'Myanmar (Burma)'),
        ('NA', 'Namibia'),
        ('NR', 'Nauru'),
        ('NP', 'Nepal'),
        ('NL', 'Netherlands'),
        ('NC', 'New Caledonia'),
        ('NZ', 'New Zealand'),
        ('NI', 'Nicaragua'),
        ('NE', 'Niger'),
        ('NG', 'Nigeria'),
        ('NU', 'Niue'),
        ('NF', 'Norfolk Island'),
        ('MP', 'Northern Mariana Islands'),
        ('NO', 'Norway'),
        ('OM', 'Oman'),
        ('PK', 'Pakistan'),
        ('PW', 'Palau'),
        ('PS', 'Palestine'),
        ('PA', 'Panama'),
        ('PG', 'Papua New Guinea'),
        ('PY', 'Paraguay'),
        ('PE', 'Peru'),
        ('PH', 'Philippines'),
        ('PN', 'Pitcairn Islands'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('PR', 'Puerto Rico'),
        ('QA', 'Qatar'),
        ('RE', 'Réunion'),
        ('RO', 'Romania'),
        ('RU', 'Russia'),
        ('RW', 'Rwanda'),
        ('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'),
        ('RS', 'Serbia'),
        ('SC', 'Seychelles'),
        ('SL', 'Sierra Leone'),
        ('SG', 'Singapore'),
        ('SX', 'Sint Maarten'),
        ('SK', 'Slovakia'),
        ('SI', 'Slovenia'),
        ('SB', 'Solomon Islands'),
        ('SO', 'Somalia'),
        ('ZA', 'South Africa'),
        ('SS', 'South Sudan'),
        ('ES', 'Spain'),
        ('LK', 'Sri Lanka'),
        ('SD', 'Sudan'),
        ('SR', 'Suriname'),
        ('SJ', 'Svalbard and Jan Mayen'),
        ('SZ', 'Swaziland'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('SY', 'Syria'),
        ('TW', 'Taiwan'),
        ('TJ', 'Tajikistan'),
        ('TZ', 'Tanzania'),
        ('TH', 'Thailand'),
        ('TL', 'Timor-Leste'),
        ('TG', 'Togo'),
        ('TK', 'Tokelau'),
        ('TO', 'Tonga'),
        ('TT', 'Trinidad and Tobago'),
        ('TN', 'Tunisia'),
        ('TR', 'Turkey'),
        ('TM', 'Turkmenistan'),
        ('TC', 'Turks and Caicos Islands'),
        ('TV', 'Tuvalu'),
        ('UG', 'Uganda'),
        ('UA', 'Ukraine'),
        ('AE', 'United Arab Emirates'),
        ('GB', 'United Kingdom'),
        ('US', 'United States'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VU', 'Vanuatu'),
        ('VA', 'Vatican City'),
        ('VE', 'Venezuela'),
        ('VN', 'Vietnam'),
        ('WF', 'Wallis and Futuna'),
        ('YE', 'Yemen'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe')
    ]

    # Convert the list into a Spark DataFrame
    df_country = spark.createDataFrame(country_data, ['country_abbreviation', 'country_name'])

    # Show the DataFrame
    df_country.write.mode("overwrite").saveAsTable(f"{in_catalog}.{in_schema}.country_lookup")

# COMMAND ----------

import os  
import pandas as pd
from io import StringIO

class LabDataSetup:
    """
    Sets up lab data by checking for the existence of a catalog, schema, volume and creating the CSV files in a staging volume.

    - Catalog, schema and volume must already exist.

    Example:
      obj = LabDataSetup('dbacademy_peter_s','default','lab_staging_files')
    """

    def __init__(self, catalog_name: str, schema_name: str, volume_name: str):
        self.catalog_name = catalog_name
        self.schema_name = schema_name
        self.volume_name = volume_name
        self.volume_path = os.path.join('/Volumes', self.catalog_name, self.schema_name, self.volume_name)

        print("Starting environment validation...")
        self._validate_environment()

        dict_of_files = {
            'employees_1.csv': self.create_csv_1_data(),
            'employees_2.csv': self.create_csv_2_data(),
            'employees_3.csv': self.create_csv_3_data()
        }

        for filename, filefunc in dict_of_files.items():
            self.create_csv_file_if_not_exists(file_name=filename, csv_data_func=filefunc)

        print(f"LabDataSetup initialized successfully in volume_path: '{self.volume_path}'")

    def _validate_environment(self):
        self._validate_catalog()
        self._validate_schema()
        self._validate_volume()

    def _validate_catalog(self):
        catalogs = spark.sql("SHOW CATALOGS").collect()
        catalog_names = [row.catalog for row in catalogs]
        if self.catalog_name in catalog_names:
            print(f"Catalog '{self.catalog_name}' exists.")
        else:
            print(f"Catalog '{self.catalog_name}' does not exist.")
            raise FileNotFoundError(f"{self.catalog_name} catalog not found.")

    def _validate_schema(self):
        full_schema_name = f"{self.catalog_name}.{self.schema_name}"
        if spark.catalog.databaseExists(full_schema_name):
            print(f"Schema '{full_schema_name}' exists.")
        else:
            print(f"Schema '{full_schema_name}' does not exist.")
            raise FileNotFoundError(f"{full_schema_name} schema not found.")

    def _validate_volume(self):
        volumes = spark.sql(f"SHOW VOLUMES IN {self.catalog_name}.{self.schema_name}").collect()
        volume_names = [v.volume_name for v in volumes]
        if self.volume_name in volume_names:
            print(f"Volume '{self.volume_name}' exists.")
        else:
            print(f"Volume '{self.volume_name}' does not exist.")
            raise FileNotFoundError(f"{self.volume_name} volume not found.")

    def check_if_file_exists(self, file_name: str) -> bool:
        file_path = os.path.join(self.volume_path, file_name)
        if os.path.exists(file_path):
            print(f"The file '{file_path}' exists.")
            return True
        else:
            print(f"The file '{file_path}' does not exist.")
            return False

    def create_csv_file(self, csv_string: str, file_to_create: str):
        df = pd.read_csv(StringIO(csv_string))
        output_path = os.path.join(self.volume_path, file_to_create)
        df.to_csv(output_path, index=False)
        print(f"Created CSV file at '{output_path}'.")

    def create_csv_file_if_not_exists(self, file_name: str, csv_data_func: callable):
        if not self.check_if_file_exists(file_name=file_name):
            print(f"Creating file '{file_name}'...")
            self.create_csv_file(csv_string=csv_data_func, file_to_create=file_name)
        else:
            print(f"File '{file_name}' already exists. Skipping creation.")

    def create_csv_1_data(self) -> str:
        return """EmployeeID,FirstName,Country,Department,Salary,HireDate,Operation,ProcessDate
null,test,test,test,9999,2025-01-01,new,2025-06-05
1,Sophia,US,Sales,72000,2025-04-01,new,2025-06-05
2,Nikos,Gr,IT,55000,2025-04-10,new,2025-06-05
3,Liam,US,Sales,69000,2025-05-03,new,2025-06-05
4,Elena,GR,IT,53000,2025-06-04,new,2025-06-05
5,James,Us,IT,60000,2025-06-05,new,2025-06-05"""

    def create_csv_2_data(self) -> str:
        return """EmployeeID,FirstName,Country,Department,Salary,HireDate,Operation,ProcessDate
6,Emily,us,Enablement,80000,2025-06-09,new,2025-06-22
7,Yannis,gR,HR,70000,2025-06-20,new,2025-06-22
3,Liam,US,Sales,100000,2025-05-03,update,2025-06-22
1,,,,,,delete,2025-06-22"""

    def create_csv_3_data(self):
        return """EmployeeID,FirstName,Country,Department,Salary,HireDate,Operation,ProcessDate
8,Panagiotis,Gr,Enablement,90000,2025-07-01,new,2025-07-22
6,,,,,,delete,2025-07-22
2,,,,,,delete,2025-07-22"""

    def copy_file(self, copy_file: str, to_target_volume: str):
        dbutils.fs.cp(f'{self.volume_path}/{copy_file}', f'{to_target_volume}/{copy_file}')
        print(f"Moving file '{self.volume_path}/{copy_file}' to '{to_target_volume}/{copy_file}'.")

    def delete_lab_staging_files(self):
        dbutils.fs.rm(self.volume_path, True)
        print(f"Deleted all files in '{self.volume_path}'.")

    def __str__(self):
        return f"LabDataSetup(catalog_name={self.catalog_name}, schema_name={self.schema_name}, volume_name={self.volume_name}, volume_path={self.volume_path})"

# COMMAND ----------

## Create volume for the lab
create_volume(in_catalog=DA.catalog_name, in_schema = 'default', volume_name = 'lab_staging_files')
create_volume(in_catalog=DA.catalog_name, in_schema = 'default', volume_name = 'lab_files')

## Create schemas for lab data
create_schemas(in_catalog = DA.catalog_name, schema_names = ['lab_1_bronze_db', 'lab_2_silver_db', 'lab_3_gold_db'])


## Create the country_lookup table if it doesn't exist
if spark.catalog.tableExists(f"{DA.catalog_name}.default.country_lookup") == False:
    create_country_lookup_table(in_catalog = DA.catalog_name, in_schema = 'default')
else:
    print(f'Table {DA.catalog_name}.default.country_lookup already exists. No action taken')

delete_source_files(f'/Volumes/{DA.catalog_name}/default/lab_files/')
delete_source_files(f'/Volumes/{DA.catalog_name}/default/lab_files_staging/')

# Example usage
LabSetup = LabDataSetup(f'{DA.catalog_name}','default','lab_staging_files')