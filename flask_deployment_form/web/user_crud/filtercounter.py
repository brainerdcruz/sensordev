# -*- coding: utf-8 -*-
"""
Created on Tue May 07 17:12:18 2019

@author: Dynaslope
"""

import analysis.querydb as qdb
import analysis.subsurface.filterdata as fsd
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
import memcache
import numpy as np
from sqlalchemy import create_engine
import time

def outlierf(dfl):
        dfl = dfl.groupby(['accel_id'])
        dfl = dfl.apply(fsd.resample_df)
        dfl = dfl.set_index('ts').groupby('accel_id').apply(fsd.outlier_filter)
        dfl = dfl.reset_index(level = ['ts'])
        dfl = dfl.reset_index(drop=True) 
        return(dfl)


def filter_counter(tsm_id = '', days_interval = 3):  
    time_now = pd.to_datetime(dt.now())
    from_time = time_now-td(days = days_interval)
    
    memc = memcache.Client(['127.0.0.1:11211'], debug=1)
    accelerometers=memc.get('DF_ACCELEROMETERS')
    accel = accelerometers[accelerometers.tsm_id ==tsm_id]

    df = qdb.get_raw_accel_data(tsm_id=tsm_id, from_time=from_time, batt =1)
    
    if not df.empty:
        count_raw = df['ts'].groupby(df.accel_id).size().rename('raw')
        
        dfv = fsd.volt_filter(df)
        count_volt = dfv['ts'].groupby(dfv.accel_id).size().rename('voltf')
        
        dfr = fsd.range_filter_accel(df)
        count_range = dfr['ts'].groupby(dfr.accel_id).size().rename('rangef')
        
        dfo = fsd.orthogonal_filter(dfr)
        count_ortho = dfo['ts'].groupby(dfo.accel_id).size().rename('orthof')
        
        dfor = outlierf(dfo)
        count_outlier = dfor['ts'].groupby(dfor.accel_id).size().rename('outlierf')
        
        dfa=pd.concat([count_raw,count_volt, count_range, count_ortho, count_outlier],axis=1)
#        dfa[np.isnan(dfa)]=0    
        
        dfa = dfa.reset_index()
    
    else:
        dfa = pd.DataFrame(columns = ['accel_id','raw','voltf','rangef','orthof','outlierf'])
        dfa = dfa.astype(float)
    
    dfa = pd.merge(accel[['accel_id']], dfa, how = 'outer', on = 'accel_id')
    dfa[(np.isnan(dfa))]=0
    dfa['ts'] = time_now
    
    dfa['percent_raw'] = dfa.raw / (48 * days_interval) * 100
    dfa['percent_voltf'] = dfa.voltf / dfa.raw * 100
    dfa['percent_rangef'] = dfa.rangef / dfa.raw * 100
    dfa['percent_orthof'] = dfa.orthof / dfa.raw * 100
    dfa['percent_outlierf'] = dfa.outlierf / dfa.raw *100
       
    dfa.ts = dfa.ts.dt.round('H')
    dfa = dfa.round(2)
    return dfa[['accel_id','ts','percent_raw','percent_voltf','percent_rangef','percent_orthof','percent_outlierf']]
def main():
    memc = memcache.Client(['127.0.0.1:11211'], debug=1)
    tsm_sensors=memc.get('DF_TSM_SENSORS')
    
    
    dffc = pd.DataFrame(columns = ['accel_id','ts','percent_raw','percent_voltf','percent_rangef','percent_orthof','percent_outlierf'])
    for i in tsm_sensors.tsm_id:
        print(i)
        dft = filter_counter(i)
        engine=create_engine('mysql+pymysql://root:senslope@192.168.150.77:3306/senslopedb', echo = False)
        dft.to_sql(name = 'data_counter', con = engine, if_exists = 'append', index = False)
        dffc = pd.concat([dffc,dft], ignore_index = True)
    
if __name__ == "__main__":
    main()
#engine=create_engine('mysql+mysqlconnector://root:senslope@192.168.150.77:3306/senslopedb', echo = False)
#dffc.to_sql(name = 'data_counter', con = engine, if_exists = 'append', index = False)


#dffc = filter_counter(1)

