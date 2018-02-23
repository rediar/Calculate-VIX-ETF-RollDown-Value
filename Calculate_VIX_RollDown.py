import pandas as pd
import datetime as dt
import urllib


def num_holidays(date1, date2, holidays):
    num = 0;
    for holiday_iter in holidays:
        if ((date1 <= holiday_iter) and (holiday_iter < date2)):
            num += 1;
    return num

def num_business_days(date1, date2, holidays):
    if (date1.weekday() > 4):
        date1 = date1 + dt.timedelta(4 - date1.weekday())
    
    total_days = int(str(date2 - date1).split(' days')[0])
    date1 = date1 - dt.timedelta(date1.weekday() - 1)
    date2 = date2 - dt.timedelta(date2.weekday() - 1)
    num_weekends = int(str(date2 - date1).split(' days')[0])/7
    return total_days - num_holidays(date1, date2, holidays) - 2*num_weekends

def calc_rolldown_single_day(date_to_calc, M1_daily_roll, M2_daily_roll, 
    holidays, Maturity_date):
    prev_mat = Maturity_date[Maturity_date <= date_to_calc][-1]
    M1_mat = Maturity_date[Maturity_date > date_to_calc][0]
    period_len = num_business_days(prev_mat, M1_mat, holidays)+1
    M1_left = float(num_business_days(date_to_calc, M1_mat,holidays))/period_len
    return M1_left*M1_daily_roll+(1-M1_left)*M2_daily_roll

def forward_28_day_rolldown(VIX, futures, holidays, Maturity_date, 
    start_date = pd.to_datetime(dt.date.today())):
    M1_mat = Maturity_date[Maturity_date > start_date][0]
    M2_mat = Maturity_date[Maturity_date > start_date][1]
    M3_mat = Maturity_date[Maturity_date > start_date][2]

    M1_daily_roll = (futures[0]/VIX-1)/num_business_days(start_date, M1_mat, 
        holidays)
    M2_daily_roll = (futures[1]/VIX-1)/num_business_days(start_date, M2_mat, 
        holidays)
    M3_daily_roll = (futures[2]/VIX-1)/num_business_days(start_date, M3_mat, 
        holidays)

    PV = 1
    for add_days in range(28):
        calc_date = start_date + dt.timedelta(add_days)
        if ((calc_date.weekday() < 5) and (calc_date not in holidays)):
            if (num_business_days(calc_date, M1_mat, holidays) > 0):
                daily_perc = calc_rolldown_single_day(calc_date, M1_daily_roll, 
                    M2_daily_roll, holidays, Maturity_date)
            else:
                daily_perc = calc_rolldown_single_day(calc_date, M2_daily_roll, 
                    M3_daily_roll, holidays, Maturity_date)
            PV += daily_perc
    return PV-1-.1/VIX


url = 'http://vixcentral.com'
Maturity_date = pd.to_datetime(['2017-12-20','2018-01-17','2018-02-14',
    '2018-03-21','2018-04-18','2018-05-16','2018-06-20','2018-07-18',
    '2018-08-22','2018-09-19','2018-10-17','2018-11-21','2018-12-19'])
holidays = pd.to_datetime(['2017-12-25','2018-01-01','2018-01-15','2018-02-19',
    '2018-03-30','2018-05-28','2018-07-04','2018-09-03','2018-11-22'])


full_site_html = urllib.urlopen(url).readlines()
delimiter_1 = 'green\',dashStyle:\'LongDash\',marker:{enabled:false},'+\
'dataLabels:{enabled:true,align:\'left\',x:5,y:4,formatter:function()'+\
'{if(this.point.x==this.series.data.length-1){return Highcharts.'+\
'numberFormat(this.y,2);}else{return null;}}},data:['
delimiter_2 = ';var last_data_var=['

for line_iter in full_site_html:
    if delimiter_1 in line_iter:
        VIX = float(line_iter.split(delimiter_1)[1].split(",")[0])
        break
for line_iter in full_site_html:
    if delimiter_2 in line_iter:
        futures = map(lambda x: float(x), 
            line_iter.split(delimiter_2)[1].split(",")[:3])
        break


start_date = pd.to_datetime(dt.date.today())
M1_mat = Maturity_date[Maturity_date > start_date][0]
M2_mat = Maturity_date[Maturity_date > start_date][1]
M3_mat = Maturity_date[Maturity_date > start_date][2]

VIX_stress = VIX;
for increment in [1, .1, .01]:
    while (forward_28_day_rolldown(VIX_stress+increment, futures, holidays, 
        Maturity_date) > 0):
        VIX_stress += increment;
    VIX_stress -= increment;


print 'VIX: ' + str(round(VIX,2))
print ''
print 'M1: ' + str(round(futures[0],2)) + ' matures ' + str(M1_mat)[:10]
print 'M2: ' + str(round(futures[1],2)) + ' matures ' + str(M2_mat)[:10]
print 'M3: ' + str(round(futures[2],2)) + ' matures ' + str(M3_mat)[:10]
print ''
print 'Forward 28 day rolldown: ' + str(round(forward_28_day_rolldown(VIX, 
    futures, holidays, Maturity_date)*100, 1)) + '%'
print 'VIX shift to flip rolldown: ' + str(VIX_stress) + ' | +' + \
str(VIX_stress - VIX) + ' | ' + str(round((VIX_stress/VIX - 1)*100, 1)) + '%'