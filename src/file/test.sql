-- 1
-- airflow
select '{{ ds }}';

-- 之前替换逻辑
select '${current_date}';
-- 新增自定义参数
current_date -> $[yyyy-MM-dd]
-- 之后在sql引用

-- 现在的替换逻辑
select '$[yyyy-MM-dd]';




-- 2
-- airflow
-- shceudle 5h
select '{{ dt_tz_add(next_execution_date, hours=-1) }}';   yyyymmdd
select '{{ ts_tz_add(next_execution_date, hours=-1) }}';   yyyymmdd HH:mm:ss
select '{{ ts_tz_add(execution_date, hours=-1) }}';   yyyymmdd HH:mm:ss

select '${custome_param}';   yyyymmdd

yyyy-MM-dd HH:mm:ss

-- airflow 的计算逻辑
next_execution_date = execution_date + shceduler_interval

-- 现在的替换逻辑
next_execution_date -> '$[yyyy-MM-dd HH:mm:ss+1]'
dt_tz_add(next_execution_date, hours=-1) -> '$[yyyy-MM-dd HH:mm:ss+1]' -> '$[yyyy-MM-dd HH:mm:ss-23/24]'


where create_date > execution_date
    and create_date < next_execution_date

-- expect
select c
-- actual
select '$[yyyy-MM-dd HH:mm:ss-23/24]';
