"""
This special case for scan LEDM calls
"""

import logging
log = logging.getLogger(__name__)

import time
from enum import Enum
from . import ledm_api
from .trees import ledm_templates
from .trees import ledm_tree
from . import trees


TIFF_HEADER = "073 073 042 000 008 000 000 000 \
012 000 \
254 000 004 000 001 000 000 000 000 000 000 000 \
000 001 004 000 001 000 000 000 064 000 000 000 \
001 001 004 000 001 000 000 000 064 000 000 000 \
002 001 003 000 001 000 000 000 008 000 000 000 \
003 001 003 000 001 000 000 000 001 000 000 000 \
006 001 003 000 001 000 000 000 001 000 000 000 \
017 001 004 000 001 000 000 000 176 000 000 000 \
022 001 004 000 001 000 000 000 064 000 000 000 \
023 001 004 000 001 000 000 000 064 000 000 000 \
026 001 005 000 001 000 000 000 158 000 000 000 \
027 001 005 000 001 000 000 000 166 000 000 000 \
040 001 003 000 001 000 000 000 002 000 000 000 \
000 000 000 000 \
044 001 000 000 001 000 000 000 \
044 001 000 000 001 000 000 000 \
000 000 "

class ScannerCalibrationType(Enum):
    """
    All supported Scanner Calibration Types
    """
    MONO_300 = 1
    COLOR_300 = 2
    COLOR_600 = 3
    COLOR_1200 = 4


class ScanPwmException(Exception):
    pass


class ScanGainException(Exception):
    pass


class ScanLedOffsetException(Exception):
    pass


class ScanExposureException(Exception):
    pass


class ScanVoltageException(Exception):
    pass


class ServoNoServoHistoryException(Exception):
    pass


class ScanReferencePostionTestException(Exception):
    pass


class Servo:
    def __init__(
            self,
            raw_data,
            count_of_servo_values,
            velocity_average,
            velocity_min,
            velocity_max,
            slew_rate,
            pwm_average,
            pwm_min,
            pwm_max,
            perr_average,
            perr_min,
            perr_max,
            motor_config_max_perr):

        self.raw_data = raw_data
        self.count_of_servo_values = count_of_servo_values
        self.velocity_average = velocity_average
        self.velocity_min = velocity_min
        self.velocity_max = velocity_max
        self.slew_rate = slew_rate
        self.pwm_average = pwm_average
        self.pwm_min = pwm_min
        self.pwm_max = pwm_max
        self.perr_average = perr_average
        self.perr_min = perr_min
        self.motor_config_max_perr = motor_config_max_perr

    def __str__(self):
        return """Scanner Servo Data:
count_of_servo_values = {0}
velocity_average = {1}
velocity_min = {2}
velocity_max = {3}
slew_rate = {4}
pwm_average = {5}
pwm_min = {6}
pwm_max = {7}
perr_average = {8}
perr_min = {9}
motor_config_max_perr = {10}

RAW DATA = \n{11}""".format(
    self.count_of_servo_values,
    self.velocity_average,
    self.velocity_min,
    self.velocity_max,
    self.slew_rate,
    self.pwm_average,
    self.pwm_min,
    self.pwm_max,
    self.perr_average,
    self.perr_min,
    self.motor_config_max_perr,
    self.raw_data)



    @classmethod
    def create_servo_data(cls, raw_data):
        """
        create servo data from raw LEDM data

        Args:
            raw_data (str): raw data from LEDM call

        Returns:
            Servo object
        """
        if "NO SERVO" in raw_data.upper():
            raise ServoNoServoHistoryException(raw_data)
        tokens = raw_data.split(",")
        count_of_servo_values = int(tokens[0])
        velocity_average = int(tokens[1])
        velocity_min = int(tokens[2])
        velocity_max = int(tokens[3])
        slew_rate = int(tokens[4])
        pwm_average = int(tokens[5])
        pwm_min = int(tokens[6])
        pwm_max = int(tokens[7])
        perr_average = int(tokens[8])
        perr_min = int(tokens[9])
        perr_max = int(tokens[10])
        motor_config_max_perr = int(tokens[11])

        servo = cls(
            raw_data,
            count_of_servo_values,
            velocity_average,
            velocity_min,
            velocity_max,
            slew_rate,
            pwm_average,
            pwm_min,
            pwm_max,
            perr_average,
            perr_min,
            perr_max,
            motor_config_max_perr
        )
        return servo


class ScannerScanlineStatistics:
    def __init_(self):
        self.red_max_value = -1                      #' 0
        self.red_max_value_pos = -1                  #' 1
        self.red_min_value = -1                      #' 2
        self.red_min_value_pos = -1                  #' 3
        self.red_max_pixel_to_pixel_diff = -1        #' 4
        self.red_max_pixel_to_pixel_diff_pos = -2    #' 5
        self.red_mean = -1                           #' 6

        self.blue_max_value = -1                     #' 7
        self.blue_max_value_pos = -1                 #' 8
        self.blue_min_value = -1                     #' 9
        self.blue_min_value_pos = -1                 #'10
        self.blue_max_pixel_to_pixel_diff = -1       #'11
        self.blue_max_pixel_to_pixel_diff_pos = -1   #'12
        self.blue_mean = -1                          #'13

        self.green_max_value = -1                    #'14
        self.green_max_value_pos = -1                #'15
        self.green_min_value = -1                    #'16
        self.green_min_value_pos = -1                #'17
        self.green_max_pixel_to_pixel_diff = -1      #'18
        self.green_max_pixel_to_pixel_diff_pos = -1  #'19
        self.green_mean = -1                         #'20

        self.red_prnu_group_one = -1                 #'21
        self.red_prnu_group_two = -1                 #'22
        self.red_prnu_group_three = -1               #'23

        self.blue_prnu_group_one = -1                #'24
        self.blue_prnu_group_two = -1                #'25
        self.blue_prnu_group_three = -1              #'26

        self.green_prnu_group_one = -1               #'27
        self.green_prnu_group_two = -1               #'28
        self.green_prnu_group_three = -1             #'29

        self.red_uncorrected_pixels_left = -1        #'30
        self.red_uncorrected_pixels_right = -1       #'31

        self.blue_uncorrected_pixels_left = -1       #'32
        self.blue_uncorrected_pixels_right = -1      #'33

        self.green_uncorrected_pixels_left = -1      #'34
        self.green_uncorrected_pixels_right = -1     #'35

        self.scan_line_width = -1                    #'36

        self.red_bad = -1                            #'37
        self.blue_bad = -1                           #'38
        self.green_bad = -1                          #'39
        self.red_bad2 = -1                           #'40
        self.blue_bad2 = -1                          #'41
        self.green_bad2 = -1                         #'42
        self.end_of_enum = -1                        #'43

    def __str__(self):
        return """Scanner Scanline Statistics:
red_max_value = {0}                   red_max_value_pos = {1}
red_min_value = {2}                   red_min_value_pos = {3}
red_max_pixel_to_pixel_diff = {4}     red_max_pixel_to_pixel_diff_pos = {5}
red_mean = {6}

blue_max_value = {7}                  blue_max_value_pos = {8}
blue_min_value = {9}                  blue_min_value_pos = {10}
blue_max_pixel_to_pixel_diff = {11}   blue_max_pixel_to_pixel_diff_pos = {12}
blue_mean = {13}

green_max_value = {14}                green_max_value_pos = {15}
green_min_value = {16}                green_min_value_pos = {17}
green_max_pixel_to_pixel_diff = {18}  green_max_pixel_to_pixel_diff_pos = {19}
green_mean = {20}

red_prnu_group_one = {21}
red_prnu_group_two = {22}
red_prnu_group_three = {23}
blue_prnu_group_one = {24}
blue_prnu_group_two = {25}
blue_prnu_group_three = {26}
green_prnu_group_one = {27}
green_prnu_group_two = {28}
green_prnu_group_three = {29}

red_uncorrected_pixels_left = {30}
red_uncorrected_pixels_right = {31}
blue_uncorrected_pixels_left = {32}
blue_uncorrected_pixels_right = {33}
green_uncorrected_pixels_left = {34}
green_uncorrected_pixels_right = {35}

scan_line_width = {36}

red_bad = {37}
blue_bad = {38}
green_bad = {39}
red_bad2 = {40}
blue_bad2 = {41}
green_bad3 = {42}""".format(
    self.red_max_value,
    self.red_max_value_pos,
    self.red_min_value,
    self.red_min_value_pos,
    self.red_max_pixel_to_pixel_diff,
    self.red_max_pixel_to_pixel_diff_pos,
    self.red_mean,
    self.blue_max_value,
    self.blue_max_value_pos,
    self.blue_min_value,
    self.blue_min_value_pos,
    self.blue_max_pixel_to_pixel_diff,
    self.blue_max_pixel_to_pixel_diff_pos,
    self.blue_mean,
    self.green_max_value,
    self.green_max_value_pos,
    self.green_min_value,
    self.green_min_value_pos,
    self.green_max_pixel_to_pixel_diff,
    self.green_max_pixel_to_pixel_diff_pos,
    self.green_mean,
    self.red_prnu_group_one,
    self.red_prnu_group_two,
    self.red_prnu_group_three,
    self.blue_prnu_group_one,
    self.blue_prnu_group_two,
    self.blue_prnu_group_three,
    self.green_prnu_group_one,
    self.green_prnu_group_two,
    self.green_prnu_group_three,
    self.red_uncorrected_pixels_left,
    self.red_uncorrected_pixels_right,
    self.blue_uncorrected_pixels_left,
    self.blue_uncorrected_pixels_right,
    self.green_uncorrected_pixels_left,
    self.green_uncorrected_pixels_right,
    self.scan_line_width,
    self.red_bad,
    self.blue_bad,
    self.green_bad,
    self.red_bad2,
    self.blue_bad2,
    self.green_bad2)

    @classmethod
    def create_raw_prnu_data(cls, raw_data):
        """
        create scanner scanline statatics data from raw data
        <cim:SCANNER-SCANLINE-STATISTICS>
         208;1210;143;279;28;880;174;205;1181;143;444;27;880;171;210;1192;146;279;31;880;175;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;2656;0;0;0;0;0;0;
        </cim:SCANNER-SCANLINE-STATISTICS>

        Args:
            raw_data (str): raw data from LEDM call

        Returns:
            ScannerScanlineStatistics object
        """
        tokens = raw_data.split(";")
        temp = cls()
        temp.red_max_value = int(tokens[0])
        temp.red_max_value_pos = int(tokens[1])
        temp.red_min_value = int(tokens[2])
        temp.red_min_value_pos = int(tokens[3])
        temp.red_max_pixel_to_pixel_diff = int(tokens[4])
        temp.red_max_pixel_to_pixel_diff_pos = int(tokens[5])
        temp.red_mean = int(tokens[6])

        temp.blue_max_value = int(tokens[7])
        temp.blue_max_value_pos = int(tokens[8])
        temp.blue_min_value = int(tokens[9])
        temp.blue_min_value_pos = int(tokens[10])
        temp.blue_max_pixel_to_pixel_diff = int(tokens[11])
        temp.blue_max_pixel_to_pixel_diff_pos = int(tokens[12])
        temp.blue_mean = int(tokens[13])
        
        temp.green_max_value = int(tokens[14])
        temp.green_max_value_pos = int(tokens[15])
        temp.green_min_value = int(tokens[16])
        temp.green_min_value_pos = int(tokens[17])
        temp.green_max_pixel_to_pixel_diff = int(tokens[18])
        temp.green_max_pixel_to_pixel_diff_pos = int(tokens[19])
        temp.green_mean = int(tokens[20])

        temp.red_prnu_group_one = int(tokens[21])
        temp.red_prnu_group_two = int(tokens[22])
        temp.red_prnu_group_three = int(tokens[23])

        temp.blue_prnu_group_one = int(tokens[24])
        temp.blue_prnu_group_two = int(tokens[25])
        temp.blue_prnu_group_three = int(tokens[26])

        temp.green_prnu_group_one = int(tokens[27])  
        temp.green_prnu_group_two = int(tokens[28])  
        temp.green_prnu_group_three = int(tokens[29])

        temp.red_uncorrected_pixels_left = int(tokens[30])
        temp.red_uncorrected_pixels_right = int(tokens[31])

        temp.blue_uncorrected_pixels_left = int(tokens[32])
        temp.blue_uncorrected_pixels_right = int(tokens[33])

        temp.green_uncorrected_pixels_left = int(tokens[34])
        temp.green_uncorrected_pixels_right = int(tokens[35])

        temp.scan_line_width = int(tokens[36])

        temp.red_bad = int(tokens[37])
        temp.blue_bad = int(tokens[38])
        temp.green_bad = int(tokens[39])
        temp.red_bad2 = int(tokens[40])
        temp.blue_bad2 = int(tokens[41])
        temp.green_bad2 = int(tokens[42])
        temp.end_of_enum = int(tokens[43]) if tokens[43] else 0

        return temp


class ScannerReferencePosition(object):

    def __init__(self, data):
        log.debug(data)
        data = data.replace(";", ",").split(",")
        self.eRefX1 = int(data[0])  # index 0
        self.eRefY1 = int(data[1])  # index 1
        self.eRefX2 = int(data[2])  # index 2
        self.eRefY2 = int(data[3])  # index 3
        self.eRefX3 = int(data[4])  # index 4
        self.eRefY3 = int(data[5])  # index 5
        self.eOriginStatus = int(data[6])  # index 6
        self.eNotch1Score = int(data[7])  # index 7
        self.eNotch1X = int(data[8])  # index 8
        self.eNotch1Y = int(data[9])  # index 9
        self.eNotch1Avg = int(data[10])  # index10
        self.eNotch2Score = int(data[11])  # index11
        self.eNotch2X = int(data[12])  # index12
        self.eNotch2Y = int(data[13])  # index13
        self.eNotch2Avg = int(data[14])  # index14
        self.eC1 = int(data[15])  # index15
        self.eC2 = int(data[16])  # index16
        self.eC3 = int(data[17])  # index17
        self.eC4 = int(data[18])  # index18
        self.eC5 = int(data[19])  # index19
        self.eC6 = int(data[20])  # index20
        self.eC7 = int(data[21])  # index21
        self.eC8 = int(data[22])  # index22
        self.eC9 = int(data[23])  # index23
        self.eC10 = int(data[24])  # index24
        self.eC11 = int(data[25])  # index25
        self.eC12 = int(data[26])  # index26
        self.eC13 = int(data[27])  # index27
        self.eC14 = int(data[28])  # index28
        self.eC15 = int(data[29])  # index29
        self.eC16 = int(data[30])  # index30
        self.eUncX1 = int(data[31])  # index31
        self.eUncY1 = int(data[32])  # index32
        self.eUncN1Score = int(data[33])  # index33
        self.eUncX2 = int(data[34])  # index34
        self.eUncY2 = int(data[35])  # index35
        self.eUncN2Score = int(data[36])  # index36
        self.eNotchFlag = int(data[37])  # index37
        self.eClampedFlag = int(data[38])  # index38

    def __str__(self):
        return """Scanner Reference Position:
            eRefX1 = {0}
            eRefY1 = {1}
            eRefX2 = {2}
            eRefY2 = {3}
            eRefX3 = {4}
            eRefY3 = {5}
            eOriginStatus = {6}
            eNotch1Score = {7}
            eNotch1X = {8}
            eNotch1Y = {9}
            eNotch1Avg = {10}
            eNotch2Score = {11}
            eNotch2X = {12}
            eNotch2Y = {13}
            eNotch2Avg = {14}
            eC1 = {15}
            eC2 = {16}
            eC3 = {17}
            eC4 = {18}
            eC5 = {19}
            eC6 = {20}
            eC7 = {21}
            eC8 = {22}
            eC9 = {23}
            eC10 = {24}
            eC11 = {25}
            eC12 = {26}
            eC13 = {27}
            eC14 = {28}
            eC15 = {29}
            eC16 = {30}
            eUncX1 = {31}
            eUncY1 = {32}
            eUncN2Score = {33}
            eNotchFlag = {34}
            eClampedFlag = {35}""".format(
                self.eRefX1,
                self.eRefY1,
                self.eRefX2,
                self.eRefY2,
                self.eRefX3,
                self.eRefY3,
                self.eOriginStatus,
                self.eNotch1Score,
                self.eNotch1X,
                self.eNotch1Y,
                self.eNotch1Avg,
                self.eNotch2Score,
                self.eNotch2X,
                self.eNotch2Y,
                self.eNotch2Avg,
                self.eC1,
                self.eC2,
                self.eC3,
                self.eC4,
                self.eC5,
                self.eC6,
                self.eC7,
                self.eC8,
                self.eC9,
                self.eC10,
                self.eC11,
                self.eC12,
                self.eC13,
                self.eC14,
                self.eC15,
                self.eC16,
                self.eUncX1,
                self.eUncY1,
                self.eUncN1Score,
                self.eUncX2,
                self.eUncY2,
                self.eUncN2Score,
                self.eNotchFlag,
                self.eClampedFlag
            )

class ScannerLampGainValue:
    def __init__(self):
        self.pwm = 0                 #' 0
        self.red_gain = -1               #' 1
        self.green_gain = -1               #' 2
        self.blue_gain = -1                #' 3
        self.red_offset = -1              #' 4
        self.green_offset = -1            #' 5
        self.blue_offset = -1             #' 6
        self.red_exposure = -1            #' 7
        self.green_exposure = -1          #' 8
        self.blue_exposure = -1           #' 9
        self.red_voltage = -1             #'10
        self.green_voltage = -1            #'11
        self.blue_voltage = -1            #'12
        self.msb_total_crc_error = -1        #'13
        self.lsb_Total_crc_eError = -1        #'14
        self.msb_s1_total_crc_error = -1     #'15
        self.lsb_s1_total_crc_error = -1     #'16
        self.msb_s2_total_crd_error = -1     #'17
        self.lsb_s2_total_crc_error = -1     #'18
        self.s1_crc_dark = -1              #'19
        self.s1_crc_gray = -1              #'20
        self.s1_crc_white = -1             #'21
        self.s2_crc_dark = -1              #'22
        self.s2_crc_gray = -1              #'23
        self.s2_crc_white = -1             #'24
        self.s2_red_max_n = -1              #'25
        self.s2_green_max_n = -1            #'26
        self.s2_blue_max_n = -1             #'27
        self.s2_mono_max_n = -1             #'28
        self.s2_red_max_d = -1              #'29
        self.s2_green_max_d = -1            #'30
        self.s2_blue_max_d = -1             #'31
        self.s2_mono_max_d = -1             #'32
        self.s2_red_min_n = -1              #'33
        self.s2_green_min_n = -1            #'34
        self.s2_blue_min_n = -1             #'35
        self.s2_mono_min_n = -1             #'36
        self.s2_red_min_d = -1              #'37
        self.s2_green_min_d = -1            #'38
        self.s2_blue_min_d = -1             #'39
        self.s2_mono_min_d = -1             #'40
        self.s2_red_avg_n = -1              #'41
        self.s2_green_avg_n = -1            #'42
        self.s2_blue_avg_n = -1             #'43
        self.s2_mono_avg_n = -1             #'44
        self.s2_red_avg_d = -1              #'45
        self.s2_green_avg_d = -1            #'46
        self.s2_blue_avg_d = -1             #'47
        self.s2_mono_avg_d = -1             #'48
        self.calibration_type_id = -1       #'49
        self.end_of_enum = -1             #'50

    def __str__(self):
        return """Scanner Lamp Gain Values:
pwm = {0}                   
red_gain = {1}
green_gain = {2}                   
blue_gain = {3}
red_offset = {4}     
green_offset = {5}
blue_offset = {6}
red_exposure = {7}                  
green_exposure = {8}
blue_exposure = {9}                  
red_voltage = {10}
green_voltage = {11}   
blue_voltage = {12}
msb_total_crc_error = {13}
lsb_Total_crc_eError = {14}                
msb_s1_total_crc_error = {15}
lsb_s1_total_crc_error = {16}
msb_s2_total_crd_error = {17}
lsb_s2_total_crc_error = {18}  
s1_crc_dark = {19}
s1_crc_gray = {20}
s1_crc_white = {21}
s2_crc_dark = {22}
s2_crc_gray = {23}
s2_crc_white = {24}
s2_red_max_n = {25}
s2_green_max_n = {26}
s2_blue_max_n = {27}
s2_mono_max_n = {28}
s2_red_max_d = {29}
s2_green_max_d = {30}
s2_blue_max_d = {31}
s2_mono_max_d = {32}
s2_red_min_n = {33}
s2_green_min_n = {34}
s2_blue_min_n = {35}
s2_mono_min_n = {36}
s2_red_min_d = {37}
s2_green_min_d = {38}
s2_blue_min_d = {39}
s2_mono_min_d = {40}
s2_red_avg_n = {41}
s2_green_avg_n = {42}
s2_blue_avg_n = {43}
s2_mono_avg_n = {44}
s2_red_avg_d = {45}
s2_green_avg_d = {46}
s2_blue_avg_d = {47}
s2_mono_avg_d = {48}
calibration_type_id = {49}""".format(
    self.pwm,
    self.red_gain,
    self.green_gain,
    self.blue_gain,
    self.red_offset,
    self.green_offset,
    self.blue_offset,
    self.red_exposure,
    self.green_exposure,
    self.blue_exposure,
    self.red_voltage,
    self.green_voltage,
    self.blue_voltage,
    self.msb_total_crc_error,
    self.lsb_Total_crc_eError,
    self.msb_s1_total_crc_error,
    self.lsb_s1_total_crc_error,
    self.msb_s2_total_crd_error,
    self.lsb_s2_total_crc_error,
    self.s1_crc_dark,
    self.s1_crc_gray,
    self.s1_crc_white,
    self.s2_crc_dark,
    self.s2_crc_gray,
    self.s2_crc_white,
    self.s2_red_max_n,
    self.s2_green_max_n,
    self.s2_blue_max_n,
    self.s2_mono_max_n,
    self.s2_red_max_d,
    self.s2_green_max_d,
    self.s2_blue_max_d,
    self.s2_mono_max_d,
    self.s2_red_min_n,
    self.s2_green_min_n,
    self.s2_blue_min_n,
    self.s2_mono_min_n,
    self.s2_red_min_d,
    self.s2_green_min_d,
    self.s2_blue_min_d,
    self.s2_mono_min_d,
    self.s2_red_avg_n,
    self.s2_green_avg_n,
    self.s2_blue_avg_n,
    self.s2_mono_avg_n,
    self.s2_red_avg_d,
    self.s2_green_avg_d,
    self.s2_blue_avg_d,
    self.s2_mono_avg_d,
    self.calibration_type_id)

    @classmethod
    def create_scanner_lamp_data(cls, data):
        """
        create scanner_lamp_data data from raw data
        <cim:SCANNER-LAMP-GAIN-VALUE>
         5;68.000;68.000;68.000;86;86;86;457;457;457;97;41;64;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;002;
        </cim:SCANNER-LAMP-GAIN-VALUE>
        """
        tokens = data.split(";")
        temp = cls()
        temp.pwm = int(tokens[0])             
        temp.red_gain = float(tokens[1])       
        temp.green_gain = float(tokens[2])      
        temp.blue_gain = float(tokens[3])       
        temp.red_offset = int(tokens[4])      
        temp.green_offset = int(tokens[5])    
        temp.blue_offset = int(tokens[6])     
        temp.red_exposure = int(tokens[7])    
        temp.green_exposure = int(tokens[8])  
        temp.blue_exposure = int(tokens[9])   
        temp.red_voltage = int(tokens[10])    
        temp.green_voltage = int(tokens[11])  
        temp.blue_voltage = int(tokens[12])   
        temp.msb_total_crc_error = int(tokens[13])
        temp.lsb_Total_crc_eError = int(tokens[14])      
        temp.msb_s1_total_crc_error = int(tokens[15]) 
        temp.lsb_s1_total_crc_error = int(tokens[16]) 
        temp.msb_s2_total_crd_error = int(tokens[17]) 
        temp.lsb_s2_total_crc_error = int(tokens[18]) 
        temp.s1_crc_dark = int(tokens[19])            
        temp.s1_crc_gray = int(tokens[20])            
        temp.s1_crc_white = int(tokens[21])           
        temp.s2_crc_dark = int(tokens[22])           
        temp.s2_crc_gray = int(tokens[23])            
        temp.s2_crc_white = int(tokens[24])          
        temp.s2_red_max_n = int(tokens[25])           
        temp.s2_green_max_n = int(tokens[26])         
        temp.s2_blue_max_n = int(tokens[27])         
        temp.s2_mono_max_n = int(tokens[28])          
        temp.s2_red_max_d = int(tokens[29])           
        temp.s2_green_max_d = int(tokens[30])         
        temp.s2_blue_max_d = int(tokens[31])         
        temp.s2_mono_max_d = int(tokens[32])          
        temp.s2_red_min_n = int(tokens[33])          
        temp.s2_green_min_n = int(tokens[34])         
        temp.s2_blue_min_n = int(tokens[35])          
        temp.s2_mono_min_n = int(tokens[36])          
        temp.s2_red_min_d = int(tokens[37])           
        temp.s2_green_min_d = int(tokens[38])         
        temp.s2_blue_min_d = int(tokens[39])         
        temp.s2_mono_min_d = int(tokens[40])          
        temp.s2_red_avg_n = int(tokens[41])           
        temp.s2_green_avg_n = int(tokens[42])         
        temp.s2_blue_avg_n = int(tokens[43])          
        temp.s2_mono_avg_n = int(tokens[44])          
        temp.s2_red_avg_d = int(tokens[45])           
        temp.s2_green_avg_d = int(tokens[46])         
        temp.s2_blue_avg_d = int(tokens[47])          
        temp.s2_mono_avg_d = int(tokens[48])          
        temp.calibration_type_id = int(tokens[49])        
        return temp

def get_servo_data():
    """
    Retreives SCANNER-SERVO-DATA Data.

    Args:

    Returns:
       Servo: Servo object
    """
    cimation_data = ledm_api.get("/DevMgmt/CIMation.xml/Servo")
    return Servo.create_servo_data(cimation_data.get("SCANNER-SERVO-DATA"))

def get_scan_reference_position():
    """
    Retreives SCANNER-REFERENCE-POSITION Data. It will communicate with unit to retrieve
    the data and return a ScannerReference object

    Args:

    Returns:
       ScannerReferencePosition: Scanner Reference object
    """
    data = ledm_api.get("CIMation")
    return ScannerReferencePosition(data.scanner_reference_position)

def get_scanner_lamp_gain_value():
    """
    208;1210;143;279;28;880;174;205;1181;143;444;27;880;171;210;1192;146;279;31;880;175;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;2656;0;0;0;0;0;0;
    """
    data = ledm_api.get("CIMation")
    return ScannerLampGainValue.create_scanner_lamp_data(data.scanner_lamp_gain_value)

def get_scanner_scanline_statistics():
    """
    208;1210;143;279;28;880;174;205;1181;143;444;27;880;171;210;1192;146;279;31;880;175;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;2656;0;0;0;0;0;0;
    """

    data = ledm_api.get("CIMation")
    return ScannerScanlineStatistics.create_raw_prnu_data(data.scanner_scanline_statistics)


def get_calibration_status(calibration_type):
    """
    Get Scanner Calibration Status

    Args:
        calibration_node (ScannerCalibrationType):  The CIMation LEDM node to set
        value (int): The value to set the node
    """
    calibrations = {
        ScannerCalibrationType.MONO_300 : "SCAN-CALIBRATION-DOWNLOAD-300-MONO",
        ScannerCalibrationType.COLOR_300: "SCAN-CALIBRATION-DOWNLOAD-300-COLOR",
        ScannerCalibrationType.COLOR_600: "SCAN-CALIBRATION-DOWNLOAD-600",
        ScannerCalibrationType.COLOR_1200: "SCAN-CALIBRATION-DOWNLOAD-1200"
    }

    calibration = calibrations[calibration_type]    
    cim = ledm_api.get("CIMation")
    return cim.get(calibration)


def initiate_calibration(calibration_type, value=512):
    """
    Initiate Scanner Calibration

    Args:
        calibration_node (ScannerCalibrationType):  The CIMation LEDM node to set
        value (int): The value to set the node
    """
    calibrations = {
        ScannerCalibrationType.MONO_300 : "SCAN-CALIBRATION-DOWNLOAD-300-MONO",
        ScannerCalibrationType.COLOR_300: "SCAN-CALIBRATION-DOWNLOAD-300-COLOR",
        ScannerCalibrationType.COLOR_600: "SCAN-CALIBRATION-DOWNLOAD-600",
        ScannerCalibrationType.COLOR_1200: "SCAN-CALIBRATION-DOWNLOAD-1200"
    }

    calibration = calibrations[calibration_type]
    scanner_cal_data = ledm_tree.LEDMTree(ledm_templates.CIMATION)
    scanner_cal_data.set(calibration, str(value))
    ledm_api.put("CIMation", scanner_cal_data)


def wait_for_calibration(time_to_wait, sleep_time=0.1):
    """
    This will poll for wait_time seconds the unit to determine when expected_value
    has been met. It will the CIMation LEDM node
    
    Args:
        time_to_wait (int): The number of seconds to wait for expected_value
        sleep_time (int): The amount of time to sleep between loops

    Returns:
        bool: True if successful else False
    """
    start_time = time.time()
    elapsed_time = time.time() - start_time
    while elapsed_time < time_to_wait:
        try:
            cimation_data = ledm_api.get("CIMation")
            if cimation_data.scanner_reference_count != "0":
                return True

        except:
            time.sleep(sleep_time)
            elapsed_time = time.time() - start_time
    return False

def scan_eduplex_config_reset():
    """
    /cim:CIMation/cim:SCANNER-SCANNER-EDUPLEX-CONFIG*;0*;PUT
    """

    cimation_data = trees.cimation.CIMation()
    cimation_data.scanner_eduplex_config = "0"
    ledm_api.put("CIMation", cimation_data)
    

def get_notch_tif_data(notch="Notch1"):
    """
    This will get the notch image data from the printer and convert it to
    tif data

    Args:
        notch (str) = is which notch to get data should be Notch1 or Notch2

    Returns:
        bytearray: tiff data

    Raises:
        ValueError: if notch is not Notch1 or Notch2
    """
    if notch not in ("Notch1", "Notch2"):
        raise ValueError(
            "incorrect argument for notch Received {} Expected: Notch1 or Notch2".format(notch))

    url = "/DevMgmt/CIMation.xml/{0}".format(notch)
    log.debug(url)
    cim_notch = ledm_api.get(url)
    node = "SCANNER-{}-DATA".format(notch.upper())
    return get_tif_data_from_pgm(raw_pgm_data=cim_notch.get(node))


def get_tif_data_from_pgm(raw_pgm_data):
    """
    It will convert pgm data of str format to tiff data
    Args:
        raw_pgm_data (str): This is pgm data from the xml tree

    Returns:
        bytearray: tiff data
    """
    n1 = raw_pgm_data.find('\n')
    magic_number = raw_pgm_data[0:n1]
    n2 = raw_pgm_data.find('\n', n1 + 1)
    width, height = raw_pgm_data[n1 + 1:n2].split(' ')
    n3 = raw_pgm_data.find('\n', n2 + 1)
    max_value = raw_pgm_data[n2 + 1:n3]
    img_data = raw_pgm_data[n3 + 1:].replace('\n', ' ').strip()
    tif_data = bytearray([int(d) for d in (TIFF_HEADER + img_data).split()])
    return tif_data