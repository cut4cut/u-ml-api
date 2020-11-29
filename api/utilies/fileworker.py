import sys
import inspect
import pandas as pd

from os import listdir
from datetime import datetime
from calendar import monthrange
from os.path import isfile, join

from xlrd import XLRDError

class Worker:

    def __init__(self, path):
        self.russian_months = [ 'январь', 'февраль', 'март',
                                'апрель', 'май', 'июнь', 'июль',
                                'август', 'сентябрь', 'октябрь',
                                'ноябрь', 'декабрь' ]
        self.stats_work_done_metres = {
                                'ВПО-3000': {'rate_fact': 34.5, 'ratio': 0.0794},
                                'ДСП-С6': {'rate_fact': 73.01025641025642, 'ratio': 0.056162467782908405},
                                'ДУОМАТИК09-32GSM': {'rate_fact': 222.38294679399732, 'ratio': 11.405802272597525},
                                'ПМГ': {'rate_fact': 100.85978260869564, 'ratio': 0.13383760049024696},
                                'ПМГ-1М': {'rate_fact': 104.51908396946564, 'ratio': 0.1374968193384223},
                                'ПУМА2012': {'rate_fact': 218.26315789473685, 'ratio': 0.2605563909774436},
                                'РПБ-01': {'rate_fact': 123.5224, 'ratio': 0.11424251221688506},
                                'СМ-2': {'rate_fact': 24.181818181818183, 'ratio': 5.352363636363637},
                                'СМ-2Б': {'rate_fact': 30.0, 'ratio': 0.03},
                                'СМ-2М': {'rate_fact': 115.0, 'ratio': 0.0575},
                                'СПП-16': {'rate_fact': 26.0, 'ratio': 0.011944444444444443},
                                'ЩОМ-1200': {'rate_fact': 164.52777777777774, 'ratio': 0.3589365079365079},
                                'ЩОМ-1200М': {'rate_fact': 243.76091370558376, 'ratio': 0.2563789878386491},
                                'ЩОМ-1600Т': {'rate_fact': 0.0, 'ratio': 0.0},
                                'ЩОМ-700': {'rate_fact': 0.0, 'ratio': 0.0},
                                'ЭЛБ-3': {'rate_fact': 144.9, 'ratio': 1.449},
                                'ЭЛБ-4': {'rate_fact': 0.0, 'ratio': 0.0},
                                'ЭЛБ-4С': {'rate_fact': 46.0, 'ratio': 0.154}
                            }
        self.path = path
        self.apvo_data = None
        self.ssps_data = None
        self.dataset = None
        self.report = None

    def filter(self, f, key_word='ССПС'):
        if f.find(key_word) > -1:
            if f.find('~$') == -1:
                return isfile(join(self.path, f))

    def parse_dt(self, dt):
        if isinstance(dt, str):
            return datetime.strptime(dt, '%d.%m.%Y')
        else:
            return dt

    def find_dt(self, string):
        return string.split()[3]
    
    def load_files(self, files, func):
        data = func(files[0])
        for item in range(1, len(files)):
            df = func(files[item])
            data = pd.concat([data, df])
        
        data = data.reset_index(drop=True)

        return data

    def parse_type(self, r):
        index = r.find('№')
        machine_type = r[:index].replace(' ','')
        #number = r[index+1:].replace(' ','')
        machine_number = r[index+1:].replace(' ','')
        return (machine_type, machine_number)

    def parse_machine(self, r):
        index = r.find('№')
        machine_type = r[:index].replace(' ','')
        number = r[index+1:].replace(' ','')
        machine_number = str(number).zfill(8)
        return (machine_type, machine_number)

    def parse_work_done(self, r):
        #print(r)
        arr = r.split(' ')
        if len(arr) < 2:
            return (None, None)
        try:
            value = float(arr[0])
            mesure = arr[1]
        except ValueError:
            return (None, None)
        return (value, mesure)

    def to_float(self, r):
        try:
            return float(r)
        except:
            return 0

    def read_apvo(self, file_name):
        file_path = self.path + '/' + file_name
        names = ['company', 'type', 'volume', 'work_area', 'work_kind', 'work_done_phis', 'work_done_pas', 'window']

        desc = pd.read_excel(file_path, nrows=2, sheet_name=0)
        #print(type(desc.iloc[1,0]), desc.iloc[1,0])
        report_dt = self.parse_dt(desc.iloc[1,0])

        year = report_dt.year
        month = report_dt.month

        max_day = monthrange(year, month)[1]

        #if self.russian_months[month-1] != file_name.split()[1]:
        #    print(self.russian_months[month-1] , file_name.split()[1])
        #    return 'ERROR'

        data = pd.read_excel(file_path, skiprows=[1,2,3,4], sheet_name=0, names=names)
        data.drop(data.tail(3).index, inplace=True)
        data['date'] = report_dt


        print('File name: {0}, first day: {1}, max days in month: {2}'.format(file_path, report_dt, max_day))

        for day in range(1, max_day):
                desc = pd.read_excel(file_path, nrows=2, sheet_name=day)
                report_dt = self.parse_dt(desc.iloc[1,0])
                #print(day, report_dt)
                day_data = pd.read_excel(file_path, skiprows=[1,2,3,4], sheet_name=day, names=names)
                day_data.drop(day_data.tail(3).index, inplace=True)
                day_data['date'] = report_dt

                data = pd.concat([data, day_data])

        data = data.reset_index(drop=True)

        return data

    def read_ssps(self, file_name):
        file_path = self.path + '/' + file_name
        names = ['company', 'machine', 'au12', 'rate_norm', 'rate_fact', 'low_rate', 'up_rate', 'residue']
        sheet_number = 1
        use_int = False
        sheet_name = str(sheet_number).zfill(2)
        #print(file_name)

        try:
            desc = pd.read_excel(file_path, nrows=1, sheet_name=sheet_name)
        except XLRDError:
            sheet_number = 0
            use_int = True
            desc = pd.read_excel(file_path, nrows=1, sheet_name=sheet_number)

        print(desc.iloc[0,0])
        dt = self.find_dt(desc.iloc[0,0])
        report_dt = self.parse_dt(dt)
        #print(file_name, dt, report_dt)

        year = report_dt.year
        month = report_dt.month

        max_day = monthrange(year, month)[1]

        #if self.russian_months[month-1] != file_name.split()[2]:
        #    print(self.russian_months[month-1] , file_name.split()[2])
        #    return 'ERROR'

        print('File name: {0}, first day: {1}, max days in month: {2}'.format(file_path, report_dt, max_day))

        if use_int:
            data = pd.read_excel(file_path, skiprows=[1,2,3,4,5,6,7], sheet_name=sheet_number, names=names)
        else:
            data = pd.read_excel(file_path, skiprows=[1,2,3,4,5,6,7], sheet_name=sheet_name, names=names)

        data['date'] = report_dt

        for day in range(sheet_number+1, max_day+sheet_number):
            try:
                if use_int:
                    desc = pd.read_excel(file_path, nrows=1, sheet_name=day)
                else:
                    sheet_name = str(day).zfill(2)
                    desc = pd.read_excel(file_path, nrows=1, sheet_name=sheet_name)

                #print(desc.iloc[0,0])
                try:
                    dt = self.find_dt(desc.iloc[0,0])
                    report_dt = self.parse_dt(dt)
                except AttributeError:
                    report_dt = dt
                
                if use_int:
                    day_data = pd.read_excel(file_path, skiprows=[1,2,3,4,5,6,7], sheet_name=day, names=names)
                else:
                    day_data = pd.read_excel(file_path, skiprows=[1,2,3,4,5,6,7], sheet_name=sheet_name, names=names)

                day_data['date'] = report_dt

                data = pd.concat([data, day_data])
            except IndexError:
                print('IndexError')

        data = data.reset_index(drop=True)

        return data

    def read_files(self):

        ssps_files  = [f for f in listdir(self.path) if self.filter(f, key_word='ССПС')]
        apvo_files  = [f for f in listdir(self.path) if self.filter(f, key_word='АПВО')]

        self.apvo_data = self.load_files(apvo_files, self.read_apvo)
        self.ssps_data = self.load_files(ssps_files, self.read_ssps)

        return (self.apvo_data, self.ssps_data)

    def make_dataset(self):
        apvo = self.apvo_data
        ssps = self.ssps_data

        apvo['machine_type'], apvo['machine_number']= zip(* apvo.type.apply(self.parse_type) ) 
        ssps['machine_type'], ssps['machine_number']= zip(* ssps.machine.apply(self.parse_machine) )
        apvo['value'], apvo['mesure'] = zip(* apvo.work_done_phis.apply(self.parse_work_done) )

        apvo = apvo[['date', 'machine_type', 'machine_number', 'company', 'type', 'volume',
                     'work_area', 'work_kind', 'value', 'mesure', 'work_done_pas', 'window']]

        ssps = ssps[['date', 'machine_type', 'machine_number', 'company', 'au12', 'rate_norm',
                     'rate_fact', 'low_rate', 'up_rate', 'residue']]

        dataset = apvo.merge(ssps, on=['date', 'machine_type', 'machine_number'], how='inner')

        dataset.value = dataset.value.apply(self.to_float)
        dataset.rate_norm = dataset.rate_norm.apply(self.to_float)
        dataset.rate_fact = dataset.rate_fact.apply(self.to_float)
        dataset.low_rate = dataset.low_rate.apply(self.to_float)
        dataset.up_rate = dataset.up_rate.apply(self.to_float)
        dataset.residue = dataset.residue.apply(self.to_float)
        #dataset['ratio'] = dataset.rate_fact / dataset.value

        self.dataset = dataset 

        return dataset

    def make_report(self):
        report = self.dataset\
                        .groupby(by=['date', 'machine_type', 'machine_number', 'mesure'])\
                        .sum()\
                        .sort_values(by=['date', 'machine_type', 'mesure'])\
                        .reset_index()

        report['avg_rate_fact'] = None 
        report['avg_ratio'] = None
        report['flg_rate'] = None 
        report['flg_ratio'] = None 

        for index, row in report.iterrows():
            if row[3] == 'м':
                avg_ratio = self.stats_work_done_metres[row[1]]['ratio']
                avg_rate_fact = self.stats_work_done_metres[row[1]]['rate_fact']

                report.at[index, 'avg_rate_fact'] = avg_rate_fact
                report.at[index, 'avg_ratio'] = avg_ratio

                if row[8]/row[4] > avg_ratio:
                    report.at[index, 'flg_ratio'] = 'Выше нормы'
                elif abs(row[8]/row[4] - avg_ratio) < 0.15:
                    report.at[index, 'flg_ratio'] = 'В норме'
                else:
                    report.at[index, 'flg_ratio'] = 'Ниже нормы' 

                if row[8] > avg_rate_fact:
                    report.at[index, 'flg_rate'] = 'Превышение'
                elif avg_rate_fact/abs(row[8] - avg_rate_fact) < 0.15:
                    report.at[index, 'flg_rate'] = 'В норме'
                else:
                    report.at[index, 'flg_rate'] = 'Ниже нормы'

        report = report.rename(columns={
            'date': 'Дата',
            'machine_type': 'Серия машины',
            'machine_number': '№ машины',
            'mesure': 'Мера',
            'value': 'Вып. объем',
            'rate_norm': 'Расход топлива по норме',
            'rate_fact': 'Расход топлива по фактический',
            'low_rate': 'Экономия',
            'up_rate': 'Перерасход',
            'residue': 'Остаток в баках на конец периода',
            'avg_rate_fact': 'Средний расход по серии',
            'avg_ratio': 'Средней расход на метр по серии',
            'flg_rate': 'Признак нарушения по расходу',
            'flg_ratio': 'Признак нарушения расход на метр'
        })

        self.report = report
        return report

    def save_report(self, report_name):
        self.report.to_excel(self.path + '/' + report_name, index=False)
        

    
        
