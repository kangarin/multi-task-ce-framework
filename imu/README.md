可调参数
1、采样率
当前采样率为400Hz，想降低采样率，可以在imu_generator中读取csv_data后，新增一行csv_data=csv_data[csv_data%F==0]，当前支持采样率为200Hz和100Hz，即F可取值为1，2，4


若是在stage1中修改，则对接受到的数据data进行上述操作即可
