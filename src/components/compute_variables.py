
import csv
from datetime import datetime
import tempfile
import shutil
import math
import numpy as np
from astropy import units as u 
from astropy.coordinates import SkyCoord, BarycentricMeanEcliptic
import pandas as pd

csv_tf = 'data/transformed_data/transferred.csv'

#! Convert date

def parse_date(old_date):
    date_obj = datetime.strptime(old_date, '%Y-%b-%d %H:%M')
    new_date = date_obj.strftime('%m/%d/%Y')
    return new_date

def rewrite_dates():
    with open(csv_tf, 'r') as original_file:
        reader = csv.reader(original_file)
        next(reader)
        rows = [[parse_date(row[0])] + row[1:] for row in reader]

    with open(csv_tf, 'w', newline='') as original_file:
        writer = csv.writer(original_file)
        writer.writerow(['Date', 'R.A._ICRF', 'DEC_ICRF', 'delta', 'deldot'])

        for row in rows:
            writer.writerow(row)

rewrite_dates()

#! Celestial coordinate convert

def ecliptic_convert():

    data = pd.read_csv(csv_tf)

    def convert_to_ecliptic(row):
        icrf_coord = SkyCoord(ra=row['R.A._ICRF']*u.deg, dec=row['DEC_ICRF']*u.deg, frame='icrs')
        ecl_coord = icrf_coord.transform_to(BarycentricMeanEcliptic)
        return pd.Series({'R.A._Ecl': ecl_coord.lon.deg, 'DEC_Ecl': ecl_coord.lat.deg})

    data[['R.A._Ecl', 'DEC_Ecl']] = data.apply(convert_to_ecliptic, axis=1)

    data.to_csv(csv_tf, index=False)

ecliptic_convert()

#! Opposition

def compute_oppositions():
    data = pd.read_csv(csv_tf)

    data['delta'] = pd.to_numeric(data['delta'])

    data['Opposition'] = data['delta'].diff()
    data['Opposition'] = data['Opposition'].apply(lambda x: 2 if x < 0 else 1)

    data['Opposition'] = data['Opposition'].mask((data['Opposition'] == 2) & (data['Opposition'].shift() == 1), 3)
    data['Opposition'] = data['Opposition'].mask((data['Opposition'] == 1) & (data['Opposition'].shift() == 2), 4)

    data['Opposition'] = data['Opposition'].mask(data.index == 0, np.nan) # Ignore first row
    data = data.iloc[1:] # Drop first row

    data.to_csv(csv_tf, index=False)

compute_oppositions()

#! Cartesian coordinates

def rewrite_dates_and_add_cartesian():
    filename = csv_tf

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='') as temp_file, open(filename, 'r', newline='') as original_file:
        reader = csv.DictReader(original_file)
        fieldnames = reader.fieldnames + ['x_ICRF', 'y_ICRF', 'z_ICRF']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            RA = float(row['R.A._ICRF'])
            DEC = float(row['DEC_ICRF'])
            r = float(row['delta'])

            RA_rad = math.radians(RA)
            DEC_rad = math.radians(DEC)

            x = r * math.cos(DEC_rad) * math.cos(RA_rad)
            y = r * math.cos(DEC_rad) * math.sin(RA_rad)
            z = r * math.sin(DEC_rad)

            row['x_ICRF'] = x
            row['y_ICRF'] = y
            row['z_ICRF'] = z

            writer.writerow(row)

    shutil.move(temp_file.name, filename)

rewrite_dates_and_add_cartesian()

#! Ecliptic coordinates

def add_ecliptic_coordinates():
    filename = csv_tf
    
    epsilon = math.radians(-23.439281)

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='') as temp_file, open(filename, 'r', newline='') as original_file:
        reader = csv.DictReader(original_file)
        fieldnames = reader.fieldnames + ['x_Ecl', 'y_Ecl', 'z_Ecl']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:

            x_ICRF = float(row['x_ICRF'])
            y_ICRF = float(row['y_ICRF'])
            z_ICRF = float(row['z_ICRF'])

            x_Ecl = x_ICRF
            y_Ecl = y_ICRF * math.cos(epsilon) - z_ICRF * math.sin(epsilon)
            z_Ecl = y_ICRF * math.sin(epsilon) + z_ICRF * math.cos(epsilon)

            row['x_Ecl'] = x_Ecl
            row['y_Ecl'] = y_Ecl
            row['z_Ecl'] = z_Ecl

            writer.writerow(row)

    shutil.move(temp_file.name, filename)

add_ecliptic_coordinates()

#! Polar coordinates

def add_polar_coordinates():
    filename = csv_tf

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='') as temp_file, open(filename, 'r', newline='') as original_file:
        reader = csv.DictReader(original_file)
        fieldnames = reader.fieldnames + ['x_Pol', 'y_Pol']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:

            x_Ecliptic = float(row['x_Ecl'])
            y_Ecliptic = float(row['y_Ecl'])

            x_Polar = math.sqrt(x_Ecliptic**2 + y_Ecliptic**2)  # r = sqrt(x^2 + y^2)
            y_Polar = math.atan2(y_Ecliptic, x_Ecliptic)  # theta = atan(y / x)

            row['x_Pol'] = x_Polar
            row['y_Pol'] = y_Polar

            writer.writerow(row)

    shutil.move(temp_file.name, filename)

add_polar_coordinates()























