# Generated from pyrobot/backend/kumir_interpreter/grammar/KumirParser.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,98,621,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,39,
        2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,45,2,46,
        7,46,2,47,7,47,2,48,7,48,2,49,7,49,2,50,7,50,2,51,7,51,2,52,7,52,
        2,53,7,53,2,54,7,54,2,55,7,55,2,56,7,56,2,57,7,57,2,58,7,58,2,59,
        7,59,2,60,7,60,2,61,7,61,2,62,7,62,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,3,1,137,8,1,1,2,1,2,1,3,1,3,1,3,5,3,144,8,3,10,3,12,3,
        147,9,3,1,4,1,4,3,4,151,8,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,
        1,5,3,5,163,8,5,1,6,1,6,1,6,5,6,168,8,6,10,6,12,6,171,9,6,1,7,1,
        7,1,7,3,7,176,8,7,1,7,1,7,1,7,1,7,3,7,182,8,7,1,8,1,8,1,8,1,8,1,
        8,1,8,1,8,3,8,191,8,8,1,8,5,8,194,8,8,10,8,12,8,197,9,8,1,9,1,9,
        1,9,3,9,202,8,9,1,10,1,10,1,10,3,10,207,8,10,1,11,1,11,1,11,5,11,
        212,8,11,10,11,12,11,215,9,11,1,12,1,12,1,12,5,12,220,8,12,10,12,
        12,12,223,9,12,1,13,1,13,1,13,5,13,228,8,13,10,13,12,13,231,9,13,
        1,14,1,14,1,14,5,14,236,8,14,10,14,12,14,239,9,14,1,15,1,15,1,15,
        5,15,244,8,15,10,15,12,15,247,9,15,1,16,1,16,1,16,5,16,252,8,16,
        10,16,12,16,255,9,16,1,17,1,17,1,18,1,18,1,18,3,18,262,8,18,1,18,
        3,18,265,8,18,1,19,1,19,1,20,1,20,1,21,1,21,1,22,1,22,1,22,1,22,
        1,23,1,23,1,23,1,23,1,23,5,23,282,8,23,10,23,12,23,285,9,23,1,23,
        1,23,3,23,289,8,23,1,23,1,23,3,23,293,8,23,1,24,1,24,1,24,5,24,298,
        8,24,10,24,12,24,301,9,24,1,25,1,25,1,25,1,26,1,26,1,26,3,26,309,
        8,26,1,27,1,27,1,27,1,27,1,27,3,27,316,8,27,1,27,3,27,319,8,27,1,
        28,3,28,322,8,28,1,28,1,28,1,28,1,29,1,29,1,29,5,29,330,8,29,10,
        29,12,29,333,9,29,1,30,4,30,336,8,30,11,30,12,30,337,1,31,4,31,341,
        8,31,11,31,12,31,342,1,32,1,32,3,32,347,8,32,1,32,1,32,1,32,3,32,
        352,8,32,1,32,3,32,355,8,32,1,32,3,32,358,8,32,1,33,1,33,1,33,3,
        33,363,8,33,1,34,1,34,1,34,3,34,368,8,34,1,35,1,35,1,36,5,36,373,
        8,36,10,36,12,36,376,9,36,1,37,1,37,1,37,1,37,1,37,3,37,383,8,37,
        1,37,3,37,386,8,37,1,38,1,38,1,38,1,38,1,38,3,38,393,8,38,1,39,1,
        39,1,39,1,39,1,39,3,39,400,8,39,3,39,402,8,39,1,39,3,39,405,8,39,
        1,40,1,40,1,40,5,40,410,8,40,10,40,12,40,413,9,40,1,41,1,41,1,41,
        1,41,3,41,419,8,41,1,42,1,42,1,42,1,42,1,42,1,42,3,42,427,8,42,1,
        42,1,42,1,43,1,43,1,43,1,43,1,43,1,44,1,44,4,44,438,8,44,11,44,12,
        44,439,1,44,1,44,3,44,444,8,44,1,44,1,44,1,45,1,45,1,45,1,46,1,46,
        1,46,1,46,1,46,1,46,1,46,1,46,3,46,459,8,46,1,46,1,46,1,46,1,46,
        1,46,3,46,466,8,46,1,47,1,47,3,47,470,8,47,1,47,1,47,1,47,3,47,475,
        8,47,1,48,1,48,1,49,1,49,1,50,1,50,1,51,1,51,1,51,1,52,1,52,1,52,
        3,52,489,8,52,1,52,3,52,492,8,52,1,53,1,53,3,53,496,8,53,1,53,1,
        53,3,53,500,8,53,1,53,1,53,3,53,504,8,53,1,53,1,53,3,53,508,8,53,
        1,53,1,53,3,53,512,8,53,1,53,1,53,3,53,516,8,53,1,53,1,53,3,53,520,
        8,53,1,53,1,53,3,53,524,8,53,1,53,1,53,3,53,528,8,53,1,53,1,53,3,
        53,532,8,53,1,53,1,53,3,53,536,8,53,1,53,3,53,539,8,53,1,54,1,54,
        1,54,1,54,5,54,545,8,54,10,54,12,54,548,9,54,1,54,1,54,1,54,1,54,
        3,54,554,8,54,1,54,3,54,557,8,54,1,55,1,55,3,55,561,8,55,1,56,1,
        56,1,56,3,56,566,8,56,1,57,1,57,1,57,3,57,571,8,57,1,58,1,58,1,58,
        3,58,576,8,58,1,59,1,59,5,59,580,8,59,10,59,12,59,583,9,59,1,60,
        1,60,4,60,587,8,60,11,60,12,60,588,1,61,1,61,1,61,1,61,3,61,595,
        8,61,1,61,3,61,598,8,61,1,61,3,61,601,8,61,1,62,5,62,604,8,62,10,
        62,12,62,607,9,62,1,62,1,62,5,62,611,8,62,10,62,12,62,614,9,62,1,
        62,3,62,617,8,62,1,62,1,62,1,62,0,0,63,0,2,4,6,8,10,12,14,16,18,
        20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,
        64,66,68,70,72,74,76,78,80,82,84,86,88,90,92,94,96,98,100,102,104,
        106,108,110,112,114,116,118,120,122,124,0,11,1,0,56,66,2,0,32,32,
        71,72,1,0,73,76,1,0,71,72,2,0,68,69,78,79,2,0,70,70,77,77,1,0,39,
        43,1,0,45,48,1,0,49,53,1,0,35,37,4,1,4,4,6,7,80,80,88,88,667,0,126,
        1,0,0,0,2,136,1,0,0,0,4,138,1,0,0,0,6,140,1,0,0,0,8,148,1,0,0,0,
        10,162,1,0,0,0,12,164,1,0,0,0,14,181,1,0,0,0,16,183,1,0,0,0,18,201,
        1,0,0,0,20,203,1,0,0,0,22,208,1,0,0,0,24,216,1,0,0,0,26,224,1,0,
        0,0,28,232,1,0,0,0,30,240,1,0,0,0,32,248,1,0,0,0,34,256,1,0,0,0,
        36,264,1,0,0,0,38,266,1,0,0,0,40,268,1,0,0,0,42,270,1,0,0,0,44,272,
        1,0,0,0,46,276,1,0,0,0,48,294,1,0,0,0,50,302,1,0,0,0,52,305,1,0,
        0,0,54,310,1,0,0,0,56,321,1,0,0,0,58,326,1,0,0,0,60,335,1,0,0,0,
        62,340,1,0,0,0,64,344,1,0,0,0,66,359,1,0,0,0,68,364,1,0,0,0,70,369,
        1,0,0,0,72,374,1,0,0,0,74,385,1,0,0,0,76,392,1,0,0,0,78,404,1,0,
        0,0,80,406,1,0,0,0,82,418,1,0,0,0,84,420,1,0,0,0,86,430,1,0,0,0,
        88,435,1,0,0,0,90,447,1,0,0,0,92,465,1,0,0,0,94,467,1,0,0,0,96,476,
        1,0,0,0,98,478,1,0,0,0,100,480,1,0,0,0,102,482,1,0,0,0,104,485,1,
        0,0,0,106,538,1,0,0,0,108,540,1,0,0,0,110,560,1,0,0,0,112,562,1,
        0,0,0,114,570,1,0,0,0,116,572,1,0,0,0,118,581,1,0,0,0,120,586,1,
        0,0,0,122,600,1,0,0,0,124,605,1,0,0,0,126,127,5,95,0,0,127,1,1,0,
        0,0,128,137,5,94,0,0,129,137,5,93,0,0,130,137,5,92,0,0,131,137,5,
        91,0,0,132,137,5,54,0,0,133,137,5,55,0,0,134,137,3,4,2,0,135,137,
        5,31,0,0,136,128,1,0,0,0,136,129,1,0,0,0,136,130,1,0,0,0,136,131,
        1,0,0,0,136,132,1,0,0,0,136,133,1,0,0,0,136,134,1,0,0,0,136,135,
        1,0,0,0,137,3,1,0,0,0,138,139,7,0,0,0,139,5,1,0,0,0,140,145,3,34,
        17,0,141,142,5,86,0,0,142,144,3,34,17,0,143,141,1,0,0,0,144,147,
        1,0,0,0,145,143,1,0,0,0,145,146,1,0,0,0,146,7,1,0,0,0,147,145,1,
        0,0,0,148,150,5,84,0,0,149,151,3,6,3,0,150,149,1,0,0,0,150,151,1,
        0,0,0,151,152,1,0,0,0,152,153,5,85,0,0,153,9,1,0,0,0,154,163,3,2,
        1,0,155,163,3,0,0,0,156,163,5,38,0,0,157,158,5,80,0,0,158,159,3,
        34,17,0,159,160,5,81,0,0,160,163,1,0,0,0,161,163,3,8,4,0,162,154,
        1,0,0,0,162,155,1,0,0,0,162,156,1,0,0,0,162,157,1,0,0,0,162,161,
        1,0,0,0,163,11,1,0,0,0,164,169,3,34,17,0,165,166,5,86,0,0,166,168,
        3,34,17,0,167,165,1,0,0,0,168,171,1,0,0,0,169,167,1,0,0,0,169,170,
        1,0,0,0,170,13,1,0,0,0,171,169,1,0,0,0,172,175,3,34,17,0,173,174,
        5,87,0,0,174,176,3,34,17,0,175,173,1,0,0,0,175,176,1,0,0,0,176,182,
        1,0,0,0,177,178,3,34,17,0,178,179,5,86,0,0,179,180,3,34,17,0,180,
        182,1,0,0,0,181,172,1,0,0,0,181,177,1,0,0,0,182,15,1,0,0,0,183,195,
        3,10,5,0,184,185,5,82,0,0,185,186,3,14,7,0,186,187,5,83,0,0,187,
        194,1,0,0,0,188,190,5,80,0,0,189,191,3,12,6,0,190,189,1,0,0,0,190,
        191,1,0,0,0,191,192,1,0,0,0,192,194,5,81,0,0,193,184,1,0,0,0,193,
        188,1,0,0,0,194,197,1,0,0,0,195,193,1,0,0,0,195,196,1,0,0,0,196,
        17,1,0,0,0,197,195,1,0,0,0,198,199,7,1,0,0,199,202,3,18,9,0,200,
        202,3,16,8,0,201,198,1,0,0,0,201,200,1,0,0,0,202,19,1,0,0,0,203,
        206,3,18,9,0,204,205,5,67,0,0,205,207,3,20,10,0,206,204,1,0,0,0,
        206,207,1,0,0,0,207,21,1,0,0,0,208,213,3,20,10,0,209,210,7,2,0,0,
        210,212,3,20,10,0,211,209,1,0,0,0,212,215,1,0,0,0,213,211,1,0,0,
        0,213,214,1,0,0,0,214,23,1,0,0,0,215,213,1,0,0,0,216,221,3,22,11,
        0,217,218,7,3,0,0,218,220,3,22,11,0,219,217,1,0,0,0,220,223,1,0,
        0,0,221,219,1,0,0,0,221,222,1,0,0,0,222,25,1,0,0,0,223,221,1,0,0,
        0,224,229,3,24,12,0,225,226,7,4,0,0,226,228,3,24,12,0,227,225,1,
        0,0,0,228,231,1,0,0,0,229,227,1,0,0,0,229,230,1,0,0,0,230,27,1,0,
        0,0,231,229,1,0,0,0,232,237,3,26,13,0,233,234,7,5,0,0,234,236,3,
        26,13,0,235,233,1,0,0,0,236,239,1,0,0,0,237,235,1,0,0,0,237,238,
        1,0,0,0,238,29,1,0,0,0,239,237,1,0,0,0,240,245,3,28,14,0,241,242,
        5,33,0,0,242,244,3,28,14,0,243,241,1,0,0,0,244,247,1,0,0,0,245,243,
        1,0,0,0,245,246,1,0,0,0,246,31,1,0,0,0,247,245,1,0,0,0,248,253,3,
        30,15,0,249,250,5,34,0,0,250,252,3,30,15,0,251,249,1,0,0,0,252,255,
        1,0,0,0,253,251,1,0,0,0,253,254,1,0,0,0,254,33,1,0,0,0,255,253,1,
        0,0,0,256,257,3,32,16,0,257,35,1,0,0,0,258,265,3,42,21,0,259,261,
        3,38,19,0,260,262,5,44,0,0,261,260,1,0,0,0,261,262,1,0,0,0,262,265,
        1,0,0,0,263,265,3,40,20,0,264,258,1,0,0,0,264,259,1,0,0,0,264,263,
        1,0,0,0,265,37,1,0,0,0,266,267,7,6,0,0,267,39,1,0,0,0,268,269,7,
        7,0,0,269,41,1,0,0,0,270,271,7,8,0,0,271,43,1,0,0,0,272,273,3,34,
        17,0,273,274,5,87,0,0,274,275,3,34,17,0,275,45,1,0,0,0,276,288,5,
        95,0,0,277,278,5,82,0,0,278,283,3,44,22,0,279,280,5,86,0,0,280,282,
        3,44,22,0,281,279,1,0,0,0,282,285,1,0,0,0,283,281,1,0,0,0,283,284,
        1,0,0,0,284,286,1,0,0,0,285,283,1,0,0,0,286,287,5,83,0,0,287,289,
        1,0,0,0,288,277,1,0,0,0,288,289,1,0,0,0,289,292,1,0,0,0,290,291,
        5,77,0,0,291,293,3,34,17,0,292,290,1,0,0,0,292,293,1,0,0,0,293,47,
        1,0,0,0,294,299,3,46,23,0,295,296,5,86,0,0,296,298,3,46,23,0,297,
        295,1,0,0,0,298,301,1,0,0,0,299,297,1,0,0,0,299,300,1,0,0,0,300,
        49,1,0,0,0,301,299,1,0,0,0,302,303,3,36,18,0,303,304,3,48,24,0,304,
        51,1,0,0,0,305,306,3,36,18,0,306,308,3,48,24,0,307,309,5,88,0,0,
        308,307,1,0,0,0,308,309,1,0,0,0,309,53,1,0,0,0,310,311,3,0,0,0,311,
        315,5,20,0,0,312,316,3,2,1,0,313,316,3,18,9,0,314,316,3,8,4,0,315,
        312,1,0,0,0,315,313,1,0,0,0,315,314,1,0,0,0,316,318,1,0,0,0,317,
        319,5,88,0,0,318,317,1,0,0,0,318,319,1,0,0,0,319,55,1,0,0,0,320,
        322,7,9,0,0,321,320,1,0,0,0,321,322,1,0,0,0,322,323,1,0,0,0,323,
        324,3,36,18,0,324,325,3,48,24,0,325,57,1,0,0,0,326,331,3,56,28,0,
        327,328,5,86,0,0,328,330,3,56,28,0,329,327,1,0,0,0,330,333,1,0,0,
        0,331,329,1,0,0,0,331,332,1,0,0,0,332,59,1,0,0,0,333,331,1,0,0,0,
        334,336,8,10,0,0,335,334,1,0,0,0,336,337,1,0,0,0,337,335,1,0,0,0,
        337,338,1,0,0,0,338,61,1,0,0,0,339,341,5,95,0,0,340,339,1,0,0,0,
        341,342,1,0,0,0,342,340,1,0,0,0,342,343,1,0,0,0,343,63,1,0,0,0,344,
        346,5,3,0,0,345,347,3,36,18,0,346,345,1,0,0,0,346,347,1,0,0,0,347,
        348,1,0,0,0,348,354,3,60,30,0,349,351,5,80,0,0,350,352,3,58,29,0,
        351,350,1,0,0,0,351,352,1,0,0,0,352,353,1,0,0,0,353,355,5,81,0,0,
        354,349,1,0,0,0,354,355,1,0,0,0,355,357,1,0,0,0,356,358,5,88,0,0,
        357,356,1,0,0,0,357,358,1,0,0,0,358,65,1,0,0,0,359,360,5,6,0,0,360,
        362,3,34,17,0,361,363,5,88,0,0,362,361,1,0,0,0,362,363,1,0,0,0,363,
        67,1,0,0,0,364,365,5,7,0,0,365,367,3,34,17,0,366,368,5,88,0,0,367,
        366,1,0,0,0,367,368,1,0,0,0,368,69,1,0,0,0,369,370,3,72,36,0,370,
        71,1,0,0,0,371,373,3,106,53,0,372,371,1,0,0,0,373,376,1,0,0,0,374,
        372,1,0,0,0,374,375,1,0,0,0,375,73,1,0,0,0,376,374,1,0,0,0,377,382,
        3,0,0,0,378,379,5,82,0,0,379,380,3,14,7,0,380,381,5,83,0,0,381,383,
        1,0,0,0,382,378,1,0,0,0,382,383,1,0,0,0,383,386,1,0,0,0,384,386,
        5,38,0,0,385,377,1,0,0,0,385,384,1,0,0,0,386,75,1,0,0,0,387,388,
        3,74,37,0,388,389,5,20,0,0,389,390,3,34,17,0,390,393,1,0,0,0,391,
        393,3,34,17,0,392,387,1,0,0,0,392,391,1,0,0,0,393,77,1,0,0,0,394,
        401,3,34,17,0,395,396,5,87,0,0,396,399,3,34,17,0,397,398,5,87,0,
        0,398,400,3,34,17,0,399,397,1,0,0,0,399,400,1,0,0,0,400,402,1,0,
        0,0,401,395,1,0,0,0,401,402,1,0,0,0,402,405,1,0,0,0,403,405,5,31,
        0,0,404,394,1,0,0,0,404,403,1,0,0,0,405,79,1,0,0,0,406,411,3,78,
        39,0,407,408,5,86,0,0,408,410,3,78,39,0,409,407,1,0,0,0,410,413,
        1,0,0,0,411,409,1,0,0,0,411,412,1,0,0,0,412,81,1,0,0,0,413,411,1,
        0,0,0,414,415,5,18,0,0,415,419,3,80,40,0,416,417,5,19,0,0,417,419,
        3,80,40,0,418,414,1,0,0,0,418,416,1,0,0,0,419,83,1,0,0,0,420,421,
        5,12,0,0,421,422,3,34,17,0,422,423,5,13,0,0,423,426,3,72,36,0,424,
        425,5,14,0,0,425,427,3,72,36,0,426,424,1,0,0,0,426,427,1,0,0,0,427,
        428,1,0,0,0,428,429,5,15,0,0,429,85,1,0,0,0,430,431,5,17,0,0,431,
        432,3,34,17,0,432,433,5,87,0,0,433,434,3,72,36,0,434,87,1,0,0,0,
        435,437,5,16,0,0,436,438,3,86,43,0,437,436,1,0,0,0,438,439,1,0,0,
        0,439,437,1,0,0,0,439,440,1,0,0,0,440,443,1,0,0,0,441,442,5,14,0,
        0,442,444,3,72,36,0,443,441,1,0,0,0,443,444,1,0,0,0,444,445,1,0,
        0,0,445,446,5,15,0,0,446,89,1,0,0,0,447,448,5,10,0,0,448,449,3,34,
        17,0,449,91,1,0,0,0,450,451,5,25,0,0,451,452,5,95,0,0,452,453,5,
        28,0,0,453,454,3,34,17,0,454,455,5,29,0,0,455,458,3,34,17,0,456,
        457,5,30,0,0,457,459,3,34,17,0,458,456,1,0,0,0,458,459,1,0,0,0,459,
        466,1,0,0,0,460,461,5,26,0,0,461,466,3,34,17,0,462,463,3,34,17,0,
        463,464,5,27,0,0,464,466,1,0,0,0,465,450,1,0,0,0,465,460,1,0,0,0,
        465,462,1,0,0,0,466,93,1,0,0,0,467,469,5,9,0,0,468,470,3,92,46,0,
        469,468,1,0,0,0,469,470,1,0,0,0,470,471,1,0,0,0,471,474,3,72,36,
        0,472,475,5,11,0,0,473,475,3,90,45,0,474,472,1,0,0,0,474,473,1,0,
        0,0,475,95,1,0,0,0,476,477,5,21,0,0,477,97,1,0,0,0,478,479,5,22,
        0,0,479,99,1,0,0,0,480,481,5,23,0,0,481,101,1,0,0,0,482,483,5,8,
        0,0,483,484,3,34,17,0,484,103,1,0,0,0,485,491,3,0,0,0,486,488,5,
        80,0,0,487,489,3,12,6,0,488,487,1,0,0,0,488,489,1,0,0,0,489,490,
        1,0,0,0,490,492,5,81,0,0,491,486,1,0,0,0,491,492,1,0,0,0,492,105,
        1,0,0,0,493,495,3,50,25,0,494,496,5,88,0,0,495,494,1,0,0,0,495,496,
        1,0,0,0,496,539,1,0,0,0,497,499,3,76,38,0,498,500,5,88,0,0,499,498,
        1,0,0,0,499,500,1,0,0,0,500,539,1,0,0,0,501,503,3,82,41,0,502,504,
        5,88,0,0,503,502,1,0,0,0,503,504,1,0,0,0,504,539,1,0,0,0,505,507,
        3,84,42,0,506,508,5,88,0,0,507,506,1,0,0,0,507,508,1,0,0,0,508,539,
        1,0,0,0,509,511,3,88,44,0,510,512,5,88,0,0,511,510,1,0,0,0,511,512,
        1,0,0,0,512,539,1,0,0,0,513,515,3,94,47,0,514,516,5,88,0,0,515,514,
        1,0,0,0,515,516,1,0,0,0,516,539,1,0,0,0,517,519,3,96,48,0,518,520,
        5,88,0,0,519,518,1,0,0,0,519,520,1,0,0,0,520,539,1,0,0,0,521,523,
        3,98,49,0,522,524,5,88,0,0,523,522,1,0,0,0,523,524,1,0,0,0,524,539,
        1,0,0,0,525,527,3,100,50,0,526,528,5,88,0,0,527,526,1,0,0,0,527,
        528,1,0,0,0,528,539,1,0,0,0,529,531,3,102,51,0,530,532,5,88,0,0,
        531,530,1,0,0,0,531,532,1,0,0,0,532,539,1,0,0,0,533,535,3,104,52,
        0,534,536,5,88,0,0,535,534,1,0,0,0,535,536,1,0,0,0,536,539,1,0,0,
        0,537,539,5,88,0,0,538,493,1,0,0,0,538,497,1,0,0,0,538,501,1,0,0,
        0,538,505,1,0,0,0,538,509,1,0,0,0,538,513,1,0,0,0,538,517,1,0,0,
        0,538,521,1,0,0,0,538,525,1,0,0,0,538,529,1,0,0,0,538,533,1,0,0,
        0,538,537,1,0,0,0,539,107,1,0,0,0,540,546,3,64,32,0,541,545,3,66,
        33,0,542,545,3,68,34,0,543,545,3,50,25,0,544,541,1,0,0,0,544,542,
        1,0,0,0,544,543,1,0,0,0,545,548,1,0,0,0,546,544,1,0,0,0,546,547,
        1,0,0,0,547,549,1,0,0,0,548,546,1,0,0,0,549,550,5,4,0,0,550,551,
        3,70,35,0,551,553,5,5,0,0,552,554,3,62,31,0,553,552,1,0,0,0,553,
        554,1,0,0,0,554,556,1,0,0,0,555,557,5,88,0,0,556,555,1,0,0,0,556,
        557,1,0,0,0,557,109,1,0,0,0,558,561,3,0,0,0,559,561,5,92,0,0,560,
        558,1,0,0,0,560,559,1,0,0,0,561,111,1,0,0,0,562,563,5,24,0,0,563,
        565,3,110,55,0,564,566,5,88,0,0,565,564,1,0,0,0,565,566,1,0,0,0,
        566,113,1,0,0,0,567,571,3,112,56,0,568,571,3,52,26,0,569,571,3,54,
        27,0,570,567,1,0,0,0,570,568,1,0,0,0,570,569,1,0,0,0,571,115,1,0,
        0,0,572,573,5,1,0,0,573,575,3,0,0,0,574,576,5,88,0,0,575,574,1,0,
        0,0,575,576,1,0,0,0,576,117,1,0,0,0,577,580,3,114,57,0,578,580,3,
        108,54,0,579,577,1,0,0,0,579,578,1,0,0,0,580,583,1,0,0,0,581,579,
        1,0,0,0,581,582,1,0,0,0,582,119,1,0,0,0,583,581,1,0,0,0,584,587,
        3,114,57,0,585,587,3,108,54,0,586,584,1,0,0,0,586,585,1,0,0,0,587,
        588,1,0,0,0,588,586,1,0,0,0,588,589,1,0,0,0,589,121,1,0,0,0,590,
        591,3,116,58,0,591,592,3,118,59,0,592,594,5,2,0,0,593,595,3,0,0,
        0,594,593,1,0,0,0,594,595,1,0,0,0,595,597,1,0,0,0,596,598,5,88,0,
        0,597,596,1,0,0,0,597,598,1,0,0,0,598,601,1,0,0,0,599,601,3,120,
        60,0,600,590,1,0,0,0,600,599,1,0,0,0,601,123,1,0,0,0,602,604,3,114,
        57,0,603,602,1,0,0,0,604,607,1,0,0,0,605,603,1,0,0,0,605,606,1,0,
        0,0,606,612,1,0,0,0,607,605,1,0,0,0,608,611,3,122,61,0,609,611,3,
        108,54,0,610,608,1,0,0,0,610,609,1,0,0,0,611,614,1,0,0,0,612,610,
        1,0,0,0,612,613,1,0,0,0,613,616,1,0,0,0,614,612,1,0,0,0,615,617,
        5,88,0,0,616,615,1,0,0,0,616,617,1,0,0,0,617,618,1,0,0,0,618,619,
        5,0,0,1,619,125,1,0,0,0,86,136,145,150,162,169,175,181,190,193,195,
        201,206,213,221,229,237,245,253,261,264,283,288,292,299,308,315,
        318,321,331,337,342,346,351,354,357,362,367,374,382,385,392,399,
        401,404,411,418,426,439,443,458,465,469,474,488,491,495,499,503,
        507,511,515,519,523,527,531,535,538,544,546,553,556,560,565,570,
        575,579,581,586,588,594,597,600,605,610,612,616
    ]

class KumirParser ( Parser ):

    grammarFileName = "KumirParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "':='", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'**'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'+'", "'-'", "'*'", "'/'", "<INVALID>", 
                     "<INVALID>", "'='", "'<'", "'>'", "'('", "')'", "'['", 
                     "']'", "'{'", "'}'", "','", "':'", "';'", "'@@'", "'@'" ]

    symbolicNames = [ "<INVALID>", "MODULE", "ENDMODULE", "ALG_HEADER", 
                      "ALG_BEGIN", "ALG_END", "PRE_CONDITION", "POST_CONDITION", 
                      "ASSERTION", "LOOP", "ENDLOOP_COND", "ENDLOOP", "IF", 
                      "THEN", "ELSE", "FI", "SWITCH", "CASE", "INPUT", "OUTPUT", 
                      "ASSIGN", "EXIT", "PAUSE", "STOP", "IMPORT", "FOR", 
                      "WHILE", "TIMES", "FROM", "TO", "STEP", "NEWLINE_CONST", 
                      "NOT", "AND", "OR", "OUT_PARAM", "IN_PARAM", "INOUT_PARAM", 
                      "RETURN_VALUE", "INTEGER_TYPE", "REAL_TYPE", "BOOLEAN_TYPE", 
                      "CHAR_TYPE", "STRING_TYPE", "TABLE_SUFFIX", "KOMPL_TYPE", 
                      "COLOR_TYPE", "SCANCODE_TYPE", "FILE_TYPE", "INTEGER_ARRAY_TYPE", 
                      "REAL_ARRAY_TYPE", "CHAR_ARRAY_TYPE", "STRING_ARRAY_TYPE", 
                      "BOOLEAN_ARRAY_TYPE", "TRUE", "FALSE", "PROZRACHNIY", 
                      "BELIY", "CHERNIY", "SERIY", "FIOLETOVIY", "SINIY", 
                      "GOLUBOY", "ZELENIY", "ZHELTIY", "ORANZHEVIY", "KRASNIY", 
                      "POWER", "GE", "LE", "NE", "PLUS", "MINUS", "MUL", 
                      "DIV", "DIV_OP", "MOD_OP", "EQ", "LT", "GT", "LPAREN", 
                      "RPAREN", "LBRACK", "RBRACK", "LBRACE", "RBRACE", 
                      "COMMA", "COLON", "SEMICOLON", "ATAT", "AT", "CHAR_LITERAL", 
                      "STRING", "REAL", "INTEGER", "ID", "LINE_COMMENT", 
                      "DOC_COMMENT", "WS" ]

    RULE_qualifiedIdentifier = 0
    RULE_literal = 1
    RULE_colorLiteral = 2
    RULE_expressionList = 3
    RULE_arrayLiteral = 4
    RULE_primaryExpression = 5
    RULE_argumentList = 6
    RULE_indexList = 7
    RULE_postfixExpression = 8
    RULE_unaryExpression = 9
    RULE_powerExpression = 10
    RULE_multiplicativeExpression = 11
    RULE_additiveExpression = 12
    RULE_relationalExpression = 13
    RULE_equalityExpression = 14
    RULE_logicalAndExpression = 15
    RULE_logicalOrExpression = 16
    RULE_expression = 17
    RULE_typeSpecifier = 18
    RULE_basicType = 19
    RULE_actorType = 20
    RULE_arrayType = 21
    RULE_arrayBounds = 22
    RULE_variableDeclarationItem = 23
    RULE_variableList = 24
    RULE_variableDeclaration = 25
    RULE_globalDeclaration = 26
    RULE_globalAssignment = 27
    RULE_parameterDeclaration = 28
    RULE_parameterList = 29
    RULE_algorithmNameTokens = 30
    RULE_algorithmName = 31
    RULE_algorithmHeader = 32
    RULE_preCondition = 33
    RULE_postCondition = 34
    RULE_algorithmBody = 35
    RULE_statementSequence = 36
    RULE_lvalue = 37
    RULE_assignmentStatement = 38
    RULE_ioArgument = 39
    RULE_ioArgumentList = 40
    RULE_ioStatement = 41
    RULE_ifStatement = 42
    RULE_caseBlock = 43
    RULE_switchStatement = 44
    RULE_endLoopCondition = 45
    RULE_loopSpecifier = 46
    RULE_loopStatement = 47
    RULE_exitStatement = 48
    RULE_pauseStatement = 49
    RULE_stopStatement = 50
    RULE_assertionStatement = 51
    RULE_procedureCallStatement = 52
    RULE_statement = 53
    RULE_algorithmDefinition = 54
    RULE_moduleName = 55
    RULE_importStatement = 56
    RULE_programItem = 57
    RULE_moduleHeader = 58
    RULE_moduleBody = 59
    RULE_implicitModuleBody = 60
    RULE_moduleDefinition = 61
    RULE_program = 62

    ruleNames =  [ "qualifiedIdentifier", "literal", "colorLiteral", "expressionList", 
                   "arrayLiteral", "primaryExpression", "argumentList", 
                   "indexList", "postfixExpression", "unaryExpression", 
                   "powerExpression", "multiplicativeExpression", "additiveExpression", 
                   "relationalExpression", "equalityExpression", "logicalAndExpression", 
                   "logicalOrExpression", "expression", "typeSpecifier", 
                   "basicType", "actorType", "arrayType", "arrayBounds", 
                   "variableDeclarationItem", "variableList", "variableDeclaration", 
                   "globalDeclaration", "globalAssignment", "parameterDeclaration", 
                   "parameterList", "algorithmNameTokens", "algorithmName", 
                   "algorithmHeader", "preCondition", "postCondition", "algorithmBody", 
                   "statementSequence", "lvalue", "assignmentStatement", 
                   "ioArgument", "ioArgumentList", "ioStatement", "ifStatement", 
                   "caseBlock", "switchStatement", "endLoopCondition", "loopSpecifier", 
                   "loopStatement", "exitStatement", "pauseStatement", "stopStatement", 
                   "assertionStatement", "procedureCallStatement", "statement", 
                   "algorithmDefinition", "moduleName", "importStatement", 
                   "programItem", "moduleHeader", "moduleBody", "implicitModuleBody", 
                   "moduleDefinition", "program" ]

    EOF = Token.EOF
    MODULE=1
    ENDMODULE=2
    ALG_HEADER=3
    ALG_BEGIN=4
    ALG_END=5
    PRE_CONDITION=6
    POST_CONDITION=7
    ASSERTION=8
    LOOP=9
    ENDLOOP_COND=10
    ENDLOOP=11
    IF=12
    THEN=13
    ELSE=14
    FI=15
    SWITCH=16
    CASE=17
    INPUT=18
    OUTPUT=19
    ASSIGN=20
    EXIT=21
    PAUSE=22
    STOP=23
    IMPORT=24
    FOR=25
    WHILE=26
    TIMES=27
    FROM=28
    TO=29
    STEP=30
    NEWLINE_CONST=31
    NOT=32
    AND=33
    OR=34
    OUT_PARAM=35
    IN_PARAM=36
    INOUT_PARAM=37
    RETURN_VALUE=38
    INTEGER_TYPE=39
    REAL_TYPE=40
    BOOLEAN_TYPE=41
    CHAR_TYPE=42
    STRING_TYPE=43
    TABLE_SUFFIX=44
    KOMPL_TYPE=45
    COLOR_TYPE=46
    SCANCODE_TYPE=47
    FILE_TYPE=48
    INTEGER_ARRAY_TYPE=49
    REAL_ARRAY_TYPE=50
    CHAR_ARRAY_TYPE=51
    STRING_ARRAY_TYPE=52
    BOOLEAN_ARRAY_TYPE=53
    TRUE=54
    FALSE=55
    PROZRACHNIY=56
    BELIY=57
    CHERNIY=58
    SERIY=59
    FIOLETOVIY=60
    SINIY=61
    GOLUBOY=62
    ZELENIY=63
    ZHELTIY=64
    ORANZHEVIY=65
    KRASNIY=66
    POWER=67
    GE=68
    LE=69
    NE=70
    PLUS=71
    MINUS=72
    MUL=73
    DIV=74
    DIV_OP=75
    MOD_OP=76
    EQ=77
    LT=78
    GT=79
    LPAREN=80
    RPAREN=81
    LBRACK=82
    RBRACK=83
    LBRACE=84
    RBRACE=85
    COMMA=86
    COLON=87
    SEMICOLON=88
    ATAT=89
    AT=90
    CHAR_LITERAL=91
    STRING=92
    REAL=93
    INTEGER=94
    ID=95
    LINE_COMMENT=96
    DOC_COMMENT=97
    WS=98

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QualifiedIdentifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(KumirParser.ID, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_qualifiedIdentifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQualifiedIdentifier" ):
                listener.enterQualifiedIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQualifiedIdentifier" ):
                listener.exitQualifiedIdentifier(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQualifiedIdentifier" ):
                return visitor.visitQualifiedIdentifier(self)
            else:
                return visitor.visitChildren(self)




    def qualifiedIdentifier(self):

        localctx = KumirParser.QualifiedIdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_qualifiedIdentifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 126
            self.match(KumirParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INTEGER(self):
            return self.getToken(KumirParser.INTEGER, 0)

        def REAL(self):
            return self.getToken(KumirParser.REAL, 0)

        def STRING(self):
            return self.getToken(KumirParser.STRING, 0)

        def CHAR_LITERAL(self):
            return self.getToken(KumirParser.CHAR_LITERAL, 0)

        def TRUE(self):
            return self.getToken(KumirParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(KumirParser.FALSE, 0)

        def colorLiteral(self):
            return self.getTypedRuleContext(KumirParser.ColorLiteralContext,0)


        def NEWLINE_CONST(self):
            return self.getToken(KumirParser.NEWLINE_CONST, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = KumirParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_literal)
        try:
            self.state = 136
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [94]:
                self.enterOuterAlt(localctx, 1)
                self.state = 128
                self.match(KumirParser.INTEGER)
                pass
            elif token in [93]:
                self.enterOuterAlt(localctx, 2)
                self.state = 129
                self.match(KumirParser.REAL)
                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 3)
                self.state = 130
                self.match(KumirParser.STRING)
                pass
            elif token in [91]:
                self.enterOuterAlt(localctx, 4)
                self.state = 131
                self.match(KumirParser.CHAR_LITERAL)
                pass
            elif token in [54]:
                self.enterOuterAlt(localctx, 5)
                self.state = 132
                self.match(KumirParser.TRUE)
                pass
            elif token in [55]:
                self.enterOuterAlt(localctx, 6)
                self.state = 133
                self.match(KumirParser.FALSE)
                pass
            elif token in [56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66]:
                self.enterOuterAlt(localctx, 7)
                self.state = 134
                self.colorLiteral()
                pass
            elif token in [31]:
                self.enterOuterAlt(localctx, 8)
                self.state = 135
                self.match(KumirParser.NEWLINE_CONST)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColorLiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PROZRACHNIY(self):
            return self.getToken(KumirParser.PROZRACHNIY, 0)

        def BELIY(self):
            return self.getToken(KumirParser.BELIY, 0)

        def CHERNIY(self):
            return self.getToken(KumirParser.CHERNIY, 0)

        def SERIY(self):
            return self.getToken(KumirParser.SERIY, 0)

        def FIOLETOVIY(self):
            return self.getToken(KumirParser.FIOLETOVIY, 0)

        def SINIY(self):
            return self.getToken(KumirParser.SINIY, 0)

        def GOLUBOY(self):
            return self.getToken(KumirParser.GOLUBOY, 0)

        def ZELENIY(self):
            return self.getToken(KumirParser.ZELENIY, 0)

        def ZHELTIY(self):
            return self.getToken(KumirParser.ZHELTIY, 0)

        def ORANZHEVIY(self):
            return self.getToken(KumirParser.ORANZHEVIY, 0)

        def KRASNIY(self):
            return self.getToken(KumirParser.KRASNIY, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_colorLiteral

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColorLiteral" ):
                listener.enterColorLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColorLiteral" ):
                listener.exitColorLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColorLiteral" ):
                return visitor.visitColorLiteral(self)
            else:
                return visitor.visitChildren(self)




    def colorLiteral(self):

        localctx = KumirParser.ColorLiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_colorLiteral)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 138
            _la = self._input.LA(1)
            if not(((((_la - 56)) & ~0x3f) == 0 and ((1 << (_la - 56)) & 2047) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.ExpressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.COMMA)
            else:
                return self.getToken(KumirParser.COMMA, i)

        def getRuleIndex(self):
            return KumirParser.RULE_expressionList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpressionList" ):
                listener.enterExpressionList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpressionList" ):
                listener.exitExpressionList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpressionList" ):
                return visitor.visitExpressionList(self)
            else:
                return visitor.visitChildren(self)




    def expressionList(self):

        localctx = KumirParser.ExpressionListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_expressionList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 140
            self.expression()
            self.state = 145
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==86:
                self.state = 141
                self.match(KumirParser.COMMA)
                self.state = 142
                self.expression()
                self.state = 147
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayLiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(KumirParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(KumirParser.RBRACE, 0)

        def expressionList(self):
            return self.getTypedRuleContext(KumirParser.ExpressionListContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_arrayLiteral

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArrayLiteral" ):
                listener.enterArrayLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArrayLiteral" ):
                listener.exitArrayLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArrayLiteral" ):
                return visitor.visitArrayLiteral(self)
            else:
                return visitor.visitChildren(self)




    def arrayLiteral(self):

        localctx = KumirParser.ArrayLiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_arrayLiteral)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 148
            self.match(KumirParser.LBRACE)
            self.state = 150
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & -18014117189124096) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & 4161864071) != 0):
                self.state = 149
                self.expressionList()


            self.state = 152
            self.match(KumirParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrimaryExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def literal(self):
            return self.getTypedRuleContext(KumirParser.LiteralContext,0)


        def qualifiedIdentifier(self):
            return self.getTypedRuleContext(KumirParser.QualifiedIdentifierContext,0)


        def RETURN_VALUE(self):
            return self.getToken(KumirParser.RETURN_VALUE, 0)

        def LPAREN(self):
            return self.getToken(KumirParser.LPAREN, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def RPAREN(self):
            return self.getToken(KumirParser.RPAREN, 0)

        def arrayLiteral(self):
            return self.getTypedRuleContext(KumirParser.ArrayLiteralContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_primaryExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrimaryExpression" ):
                listener.enterPrimaryExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrimaryExpression" ):
                listener.exitPrimaryExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrimaryExpression" ):
                return visitor.visitPrimaryExpression(self)
            else:
                return visitor.visitChildren(self)




    def primaryExpression(self):

        localctx = KumirParser.PrimaryExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_primaryExpression)
        try:
            self.state = 162
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [31, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 91, 92, 93, 94]:
                self.enterOuterAlt(localctx, 1)
                self.state = 154
                self.literal()
                pass
            elif token in [95]:
                self.enterOuterAlt(localctx, 2)
                self.state = 155
                self.qualifiedIdentifier()
                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 3)
                self.state = 156
                self.match(KumirParser.RETURN_VALUE)
                pass
            elif token in [80]:
                self.enterOuterAlt(localctx, 4)
                self.state = 157
                self.match(KumirParser.LPAREN)
                self.state = 158
                self.expression()
                self.state = 159
                self.match(KumirParser.RPAREN)
                pass
            elif token in [84]:
                self.enterOuterAlt(localctx, 5)
                self.state = 161
                self.arrayLiteral()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgumentListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.ExpressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.COMMA)
            else:
                return self.getToken(KumirParser.COMMA, i)

        def getRuleIndex(self):
            return KumirParser.RULE_argumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArgumentList" ):
                listener.enterArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArgumentList" ):
                listener.exitArgumentList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgumentList" ):
                return visitor.visitArgumentList(self)
            else:
                return visitor.visitChildren(self)




    def argumentList(self):

        localctx = KumirParser.ArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_argumentList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 164
            self.expression()
            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==86:
                self.state = 165
                self.match(KumirParser.COMMA)
                self.state = 166
                self.expression()
                self.state = 171
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IndexListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.ExpressionContext,i)


        def COLON(self):
            return self.getToken(KumirParser.COLON, 0)

        def COMMA(self):
            return self.getToken(KumirParser.COMMA, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_indexList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIndexList" ):
                listener.enterIndexList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIndexList" ):
                listener.exitIndexList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIndexList" ):
                return visitor.visitIndexList(self)
            else:
                return visitor.visitChildren(self)




    def indexList(self):

        localctx = KumirParser.IndexListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_indexList)
        self._la = 0 # Token type
        try:
            self.state = 181
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 172
                self.expression()
                self.state = 175
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==87:
                    self.state = 173
                    self.match(KumirParser.COLON)
                    self.state = 174
                    self.expression()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 177
                self.expression()
                self.state = 178
                self.match(KumirParser.COMMA)
                self.state = 179
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PostfixExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def primaryExpression(self):
            return self.getTypedRuleContext(KumirParser.PrimaryExpressionContext,0)


        def LBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.LBRACK)
            else:
                return self.getToken(KumirParser.LBRACK, i)

        def indexList(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.IndexListContext)
            else:
                return self.getTypedRuleContext(KumirParser.IndexListContext,i)


        def RBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.RBRACK)
            else:
                return self.getToken(KumirParser.RBRACK, i)

        def LPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.LPAREN)
            else:
                return self.getToken(KumirParser.LPAREN, i)

        def RPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.RPAREN)
            else:
                return self.getToken(KumirParser.RPAREN, i)

        def argumentList(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ArgumentListContext)
            else:
                return self.getTypedRuleContext(KumirParser.ArgumentListContext,i)


        def getRuleIndex(self):
            return KumirParser.RULE_postfixExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPostfixExpression" ):
                listener.enterPostfixExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPostfixExpression" ):
                listener.exitPostfixExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPostfixExpression" ):
                return visitor.visitPostfixExpression(self)
            else:
                return visitor.visitChildren(self)




    def postfixExpression(self):

        localctx = KumirParser.PostfixExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_postfixExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 183
            self.primaryExpression()
            self.state = 195
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 193
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [82]:
                        self.state = 184
                        self.match(KumirParser.LBRACK)
                        self.state = 185
                        self.indexList()
                        self.state = 186
                        self.match(KumirParser.RBRACK)
                        pass
                    elif token in [80]:
                        self.state = 188
                        self.match(KumirParser.LPAREN)
                        self.state = 190
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if (((_la) & ~0x3f) == 0 and ((1 << _la) & -18014117189124096) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & 4161864071) != 0):
                            self.state = 189
                            self.argumentList()


                        self.state = 192
                        self.match(KumirParser.RPAREN)
                        pass
                    else:
                        raise NoViableAltException(self)
             
                self.state = 197
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UnaryExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def unaryExpression(self):
            return self.getTypedRuleContext(KumirParser.UnaryExpressionContext,0)


        def PLUS(self):
            return self.getToken(KumirParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(KumirParser.MINUS, 0)

        def NOT(self):
            return self.getToken(KumirParser.NOT, 0)

        def postfixExpression(self):
            return self.getTypedRuleContext(KumirParser.PostfixExpressionContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_unaryExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnaryExpression" ):
                listener.enterUnaryExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnaryExpression" ):
                listener.exitUnaryExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnaryExpression" ):
                return visitor.visitUnaryExpression(self)
            else:
                return visitor.visitChildren(self)




    def unaryExpression(self):

        localctx = KumirParser.UnaryExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_unaryExpression)
        self._la = 0 # Token type
        try:
            self.state = 201
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [32, 71, 72]:
                self.enterOuterAlt(localctx, 1)
                self.state = 198
                _la = self._input.LA(1)
                if not(((((_la - 32)) & ~0x3f) == 0 and ((1 << (_la - 32)) & 1649267441665) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 199
                self.unaryExpression()
                pass
            elif token in [31, 38, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 80, 84, 91, 92, 93, 94, 95]:
                self.enterOuterAlt(localctx, 2)
                self.state = 200
                self.postfixExpression()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PowerExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def unaryExpression(self):
            return self.getTypedRuleContext(KumirParser.UnaryExpressionContext,0)


        def POWER(self):
            return self.getToken(KumirParser.POWER, 0)

        def powerExpression(self):
            return self.getTypedRuleContext(KumirParser.PowerExpressionContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_powerExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPowerExpression" ):
                listener.enterPowerExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPowerExpression" ):
                listener.exitPowerExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPowerExpression" ):
                return visitor.visitPowerExpression(self)
            else:
                return visitor.visitChildren(self)




    def powerExpression(self):

        localctx = KumirParser.PowerExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_powerExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 203
            self.unaryExpression()
            self.state = 206
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==67:
                self.state = 204
                self.match(KumirParser.POWER)
                self.state = 205
                self.powerExpression()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MultiplicativeExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def powerExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.PowerExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.PowerExpressionContext,i)


        def MUL(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.MUL)
            else:
                return self.getToken(KumirParser.MUL, i)

        def DIV(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.DIV)
            else:
                return self.getToken(KumirParser.DIV, i)

        def DIV_OP(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.DIV_OP)
            else:
                return self.getToken(KumirParser.DIV_OP, i)

        def MOD_OP(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.MOD_OP)
            else:
                return self.getToken(KumirParser.MOD_OP, i)

        def getRuleIndex(self):
            return KumirParser.RULE_multiplicativeExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMultiplicativeExpression" ):
                listener.enterMultiplicativeExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMultiplicativeExpression" ):
                listener.exitMultiplicativeExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMultiplicativeExpression" ):
                return visitor.visitMultiplicativeExpression(self)
            else:
                return visitor.visitChildren(self)




    def multiplicativeExpression(self):

        localctx = KumirParser.MultiplicativeExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_multiplicativeExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 208
            self.powerExpression()
            self.state = 213
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 73)) & ~0x3f) == 0 and ((1 << (_la - 73)) & 15) != 0):
                self.state = 209
                _la = self._input.LA(1)
                if not(((((_la - 73)) & ~0x3f) == 0 and ((1 << (_la - 73)) & 15) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 210
                self.powerExpression()
                self.state = 215
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AdditiveExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def multiplicativeExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.MultiplicativeExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.MultiplicativeExpressionContext,i)


        def PLUS(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.PLUS)
            else:
                return self.getToken(KumirParser.PLUS, i)

        def MINUS(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.MINUS)
            else:
                return self.getToken(KumirParser.MINUS, i)

        def getRuleIndex(self):
            return KumirParser.RULE_additiveExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAdditiveExpression" ):
                listener.enterAdditiveExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAdditiveExpression" ):
                listener.exitAdditiveExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAdditiveExpression" ):
                return visitor.visitAdditiveExpression(self)
            else:
                return visitor.visitChildren(self)




    def additiveExpression(self):

        localctx = KumirParser.AdditiveExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_additiveExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 216
            self.multiplicativeExpression()
            self.state = 221
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,13,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 217
                    _la = self._input.LA(1)
                    if not(_la==71 or _la==72):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 218
                    self.multiplicativeExpression() 
                self.state = 223
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelationalExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def additiveExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.AdditiveExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.AdditiveExpressionContext,i)


        def LT(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.LT)
            else:
                return self.getToken(KumirParser.LT, i)

        def GT(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.GT)
            else:
                return self.getToken(KumirParser.GT, i)

        def LE(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.LE)
            else:
                return self.getToken(KumirParser.LE, i)

        def GE(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.GE)
            else:
                return self.getToken(KumirParser.GE, i)

        def getRuleIndex(self):
            return KumirParser.RULE_relationalExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationalExpression" ):
                listener.enterRelationalExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationalExpression" ):
                listener.exitRelationalExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationalExpression" ):
                return visitor.visitRelationalExpression(self)
            else:
                return visitor.visitChildren(self)




    def relationalExpression(self):

        localctx = KumirParser.RelationalExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_relationalExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 224
            self.additiveExpression()
            self.state = 229
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & 3075) != 0):
                self.state = 225
                _la = self._input.LA(1)
                if not(((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & 3075) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 226
                self.additiveExpression()
                self.state = 231
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EqualityExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def relationalExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.RelationalExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.RelationalExpressionContext,i)


        def EQ(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.EQ)
            else:
                return self.getToken(KumirParser.EQ, i)

        def NE(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.NE)
            else:
                return self.getToken(KumirParser.NE, i)

        def getRuleIndex(self):
            return KumirParser.RULE_equalityExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEqualityExpression" ):
                listener.enterEqualityExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEqualityExpression" ):
                listener.exitEqualityExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEqualityExpression" ):
                return visitor.visitEqualityExpression(self)
            else:
                return visitor.visitChildren(self)




    def equalityExpression(self):

        localctx = KumirParser.EqualityExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_equalityExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 232
            self.relationalExpression()
            self.state = 237
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==70 or _la==77:
                self.state = 233
                _la = self._input.LA(1)
                if not(_la==70 or _la==77):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 234
                self.relationalExpression()
                self.state = 239
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LogicalAndExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def equalityExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.EqualityExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.EqualityExpressionContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.AND)
            else:
                return self.getToken(KumirParser.AND, i)

        def getRuleIndex(self):
            return KumirParser.RULE_logicalAndExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalAndExpression" ):
                listener.enterLogicalAndExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalAndExpression" ):
                listener.exitLogicalAndExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalAndExpression" ):
                return visitor.visitLogicalAndExpression(self)
            else:
                return visitor.visitChildren(self)




    def logicalAndExpression(self):

        localctx = KumirParser.LogicalAndExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_logicalAndExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 240
            self.equalityExpression()
            self.state = 245
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==33:
                self.state = 241
                self.match(KumirParser.AND)
                self.state = 242
                self.equalityExpression()
                self.state = 247
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LogicalOrExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def logicalAndExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.LogicalAndExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.LogicalAndExpressionContext,i)


        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.OR)
            else:
                return self.getToken(KumirParser.OR, i)

        def getRuleIndex(self):
            return KumirParser.RULE_logicalOrExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalOrExpression" ):
                listener.enterLogicalOrExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalOrExpression" ):
                listener.exitLogicalOrExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalOrExpression" ):
                return visitor.visitLogicalOrExpression(self)
            else:
                return visitor.visitChildren(self)




    def logicalOrExpression(self):

        localctx = KumirParser.LogicalOrExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_logicalOrExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 248
            self.logicalAndExpression()
            self.state = 253
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==34:
                self.state = 249
                self.match(KumirParser.OR)
                self.state = 250
                self.logicalAndExpression()
                self.state = 255
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def logicalOrExpression(self):
            return self.getTypedRuleContext(KumirParser.LogicalOrExpressionContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression" ):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = KumirParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 256
            self.logicalOrExpression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TypeSpecifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def arrayType(self):
            return self.getTypedRuleContext(KumirParser.ArrayTypeContext,0)


        def basicType(self):
            return self.getTypedRuleContext(KumirParser.BasicTypeContext,0)


        def TABLE_SUFFIX(self):
            return self.getToken(KumirParser.TABLE_SUFFIX, 0)

        def actorType(self):
            return self.getTypedRuleContext(KumirParser.ActorTypeContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_typeSpecifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTypeSpecifier" ):
                listener.enterTypeSpecifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTypeSpecifier" ):
                listener.exitTypeSpecifier(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTypeSpecifier" ):
                return visitor.visitTypeSpecifier(self)
            else:
                return visitor.visitChildren(self)




    def typeSpecifier(self):

        localctx = KumirParser.TypeSpecifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_typeSpecifier)
        try:
            self.state = 264
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [49, 50, 51, 52, 53]:
                self.enterOuterAlt(localctx, 1)
                self.state = 258
                self.arrayType()
                pass
            elif token in [39, 40, 41, 42, 43]:
                self.enterOuterAlt(localctx, 2)
                self.state = 259
                self.basicType()
                self.state = 261
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,18,self._ctx)
                if la_ == 1:
                    self.state = 260
                    self.match(KumirParser.TABLE_SUFFIX)


                pass
            elif token in [45, 46, 47, 48]:
                self.enterOuterAlt(localctx, 3)
                self.state = 263
                self.actorType()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BasicTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INTEGER_TYPE(self):
            return self.getToken(KumirParser.INTEGER_TYPE, 0)

        def REAL_TYPE(self):
            return self.getToken(KumirParser.REAL_TYPE, 0)

        def BOOLEAN_TYPE(self):
            return self.getToken(KumirParser.BOOLEAN_TYPE, 0)

        def CHAR_TYPE(self):
            return self.getToken(KumirParser.CHAR_TYPE, 0)

        def STRING_TYPE(self):
            return self.getToken(KumirParser.STRING_TYPE, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_basicType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBasicType" ):
                listener.enterBasicType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBasicType" ):
                listener.exitBasicType(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBasicType" ):
                return visitor.visitBasicType(self)
            else:
                return visitor.visitChildren(self)




    def basicType(self):

        localctx = KumirParser.BasicTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_basicType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 266
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 17042430230528) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ActorTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KOMPL_TYPE(self):
            return self.getToken(KumirParser.KOMPL_TYPE, 0)

        def COLOR_TYPE(self):
            return self.getToken(KumirParser.COLOR_TYPE, 0)

        def SCANCODE_TYPE(self):
            return self.getToken(KumirParser.SCANCODE_TYPE, 0)

        def FILE_TYPE(self):
            return self.getToken(KumirParser.FILE_TYPE, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_actorType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterActorType" ):
                listener.enterActorType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitActorType" ):
                listener.exitActorType(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitActorType" ):
                return visitor.visitActorType(self)
            else:
                return visitor.visitChildren(self)




    def actorType(self):

        localctx = KumirParser.ActorTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_actorType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 268
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 527765581332480) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INTEGER_ARRAY_TYPE(self):
            return self.getToken(KumirParser.INTEGER_ARRAY_TYPE, 0)

        def REAL_ARRAY_TYPE(self):
            return self.getToken(KumirParser.REAL_ARRAY_TYPE, 0)

        def BOOLEAN_ARRAY_TYPE(self):
            return self.getToken(KumirParser.BOOLEAN_ARRAY_TYPE, 0)

        def CHAR_ARRAY_TYPE(self):
            return self.getToken(KumirParser.CHAR_ARRAY_TYPE, 0)

        def STRING_ARRAY_TYPE(self):
            return self.getToken(KumirParser.STRING_ARRAY_TYPE, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_arrayType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArrayType" ):
                listener.enterArrayType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArrayType" ):
                listener.exitArrayType(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArrayType" ):
                return visitor.visitArrayType(self)
            else:
                return visitor.visitChildren(self)




    def arrayType(self):

        localctx = KumirParser.ArrayTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_arrayType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 270
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 17451448556060672) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayBoundsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.ExpressionContext,i)


        def COLON(self):
            return self.getToken(KumirParser.COLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_arrayBounds

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArrayBounds" ):
                listener.enterArrayBounds(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArrayBounds" ):
                listener.exitArrayBounds(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArrayBounds" ):
                return visitor.visitArrayBounds(self)
            else:
                return visitor.visitChildren(self)




    def arrayBounds(self):

        localctx = KumirParser.ArrayBoundsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_arrayBounds)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 272
            self.expression()
            self.state = 273
            self.match(KumirParser.COLON)
            self.state = 274
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableDeclarationItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(KumirParser.ID, 0)

        def LBRACK(self):
            return self.getToken(KumirParser.LBRACK, 0)

        def arrayBounds(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ArrayBoundsContext)
            else:
                return self.getTypedRuleContext(KumirParser.ArrayBoundsContext,i)


        def RBRACK(self):
            return self.getToken(KumirParser.RBRACK, 0)

        def EQ(self):
            return self.getToken(KumirParser.EQ, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.COMMA)
            else:
                return self.getToken(KumirParser.COMMA, i)

        def getRuleIndex(self):
            return KumirParser.RULE_variableDeclarationItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariableDeclarationItem" ):
                listener.enterVariableDeclarationItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariableDeclarationItem" ):
                listener.exitVariableDeclarationItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariableDeclarationItem" ):
                return visitor.visitVariableDeclarationItem(self)
            else:
                return visitor.visitChildren(self)




    def variableDeclarationItem(self):

        localctx = KumirParser.VariableDeclarationItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_variableDeclarationItem)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 276
            self.match(KumirParser.ID)
            self.state = 288
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==82:
                self.state = 277
                self.match(KumirParser.LBRACK)
                self.state = 278
                self.arrayBounds()
                self.state = 283
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==86:
                    self.state = 279
                    self.match(KumirParser.COMMA)
                    self.state = 280
                    self.arrayBounds()
                    self.state = 285
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 286
                self.match(KumirParser.RBRACK)


            self.state = 292
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==77:
                self.state = 290
                self.match(KumirParser.EQ)
                self.state = 291
                self.expression()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variableDeclarationItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.VariableDeclarationItemContext)
            else:
                return self.getTypedRuleContext(KumirParser.VariableDeclarationItemContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.COMMA)
            else:
                return self.getToken(KumirParser.COMMA, i)

        def getRuleIndex(self):
            return KumirParser.RULE_variableList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariableList" ):
                listener.enterVariableList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariableList" ):
                listener.exitVariableList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariableList" ):
                return visitor.visitVariableList(self)
            else:
                return visitor.visitChildren(self)




    def variableList(self):

        localctx = KumirParser.VariableListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_variableList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 294
            self.variableDeclarationItem()
            self.state = 299
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,23,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 295
                    self.match(KumirParser.COMMA)
                    self.state = 296
                    self.variableDeclarationItem() 
                self.state = 301
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,23,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableDeclarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typeSpecifier(self):
            return self.getTypedRuleContext(KumirParser.TypeSpecifierContext,0)


        def variableList(self):
            return self.getTypedRuleContext(KumirParser.VariableListContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_variableDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariableDeclaration" ):
                listener.enterVariableDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariableDeclaration" ):
                listener.exitVariableDeclaration(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariableDeclaration" ):
                return visitor.visitVariableDeclaration(self)
            else:
                return visitor.visitChildren(self)




    def variableDeclaration(self):

        localctx = KumirParser.VariableDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_variableDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 302
            self.typeSpecifier()
            self.state = 303
            self.variableList()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GlobalDeclarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typeSpecifier(self):
            return self.getTypedRuleContext(KumirParser.TypeSpecifierContext,0)


        def variableList(self):
            return self.getTypedRuleContext(KumirParser.VariableListContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_globalDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGlobalDeclaration" ):
                listener.enterGlobalDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGlobalDeclaration" ):
                listener.exitGlobalDeclaration(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGlobalDeclaration" ):
                return visitor.visitGlobalDeclaration(self)
            else:
                return visitor.visitChildren(self)




    def globalDeclaration(self):

        localctx = KumirParser.GlobalDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_globalDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 305
            self.typeSpecifier()
            self.state = 306
            self.variableList()
            self.state = 308
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,24,self._ctx)
            if la_ == 1:
                self.state = 307
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GlobalAssignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def qualifiedIdentifier(self):
            return self.getTypedRuleContext(KumirParser.QualifiedIdentifierContext,0)


        def ASSIGN(self):
            return self.getToken(KumirParser.ASSIGN, 0)

        def literal(self):
            return self.getTypedRuleContext(KumirParser.LiteralContext,0)


        def unaryExpression(self):
            return self.getTypedRuleContext(KumirParser.UnaryExpressionContext,0)


        def arrayLiteral(self):
            return self.getTypedRuleContext(KumirParser.ArrayLiteralContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_globalAssignment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGlobalAssignment" ):
                listener.enterGlobalAssignment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGlobalAssignment" ):
                listener.exitGlobalAssignment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGlobalAssignment" ):
                return visitor.visitGlobalAssignment(self)
            else:
                return visitor.visitChildren(self)




    def globalAssignment(self):

        localctx = KumirParser.GlobalAssignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_globalAssignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 310
            self.qualifiedIdentifier()
            self.state = 311
            self.match(KumirParser.ASSIGN)
            self.state = 315
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,25,self._ctx)
            if la_ == 1:
                self.state = 312
                self.literal()
                pass

            elif la_ == 2:
                self.state = 313
                self.unaryExpression()
                pass

            elif la_ == 3:
                self.state = 314
                self.arrayLiteral()
                pass


            self.state = 318
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
            if la_ == 1:
                self.state = 317
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParameterDeclarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typeSpecifier(self):
            return self.getTypedRuleContext(KumirParser.TypeSpecifierContext,0)


        def variableList(self):
            return self.getTypedRuleContext(KumirParser.VariableListContext,0)


        def IN_PARAM(self):
            return self.getToken(KumirParser.IN_PARAM, 0)

        def OUT_PARAM(self):
            return self.getToken(KumirParser.OUT_PARAM, 0)

        def INOUT_PARAM(self):
            return self.getToken(KumirParser.INOUT_PARAM, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_parameterDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameterDeclaration" ):
                listener.enterParameterDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameterDeclaration" ):
                listener.exitParameterDeclaration(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParameterDeclaration" ):
                return visitor.visitParameterDeclaration(self)
            else:
                return visitor.visitChildren(self)




    def parameterDeclaration(self):

        localctx = KumirParser.ParameterDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_parameterDeclaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 321
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 240518168576) != 0):
                self.state = 320
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 240518168576) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 323
            self.typeSpecifier()
            self.state = 324
            self.variableList()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParameterListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def parameterDeclaration(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ParameterDeclarationContext)
            else:
                return self.getTypedRuleContext(KumirParser.ParameterDeclarationContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.COMMA)
            else:
                return self.getToken(KumirParser.COMMA, i)

        def getRuleIndex(self):
            return KumirParser.RULE_parameterList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameterList" ):
                listener.enterParameterList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameterList" ):
                listener.exitParameterList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParameterList" ):
                return visitor.visitParameterList(self)
            else:
                return visitor.visitChildren(self)




    def parameterList(self):

        localctx = KumirParser.ParameterListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_parameterList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 326
            self.parameterDeclaration()
            self.state = 331
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==86:
                self.state = 327
                self.match(KumirParser.COMMA)
                self.state = 328
                self.parameterDeclaration()
                self.state = 333
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AlgorithmNameTokensContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.LPAREN)
            else:
                return self.getToken(KumirParser.LPAREN, i)

        def ALG_BEGIN(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.ALG_BEGIN)
            else:
                return self.getToken(KumirParser.ALG_BEGIN, i)

        def PRE_CONDITION(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.PRE_CONDITION)
            else:
                return self.getToken(KumirParser.PRE_CONDITION, i)

        def POST_CONDITION(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.POST_CONDITION)
            else:
                return self.getToken(KumirParser.POST_CONDITION, i)

        def SEMICOLON(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.SEMICOLON)
            else:
                return self.getToken(KumirParser.SEMICOLON, i)

        def EOF(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.EOF)
            else:
                return self.getToken(KumirParser.EOF, i)

        def getRuleIndex(self):
            return KumirParser.RULE_algorithmNameTokens

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAlgorithmNameTokens" ):
                listener.enterAlgorithmNameTokens(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAlgorithmNameTokens" ):
                listener.exitAlgorithmNameTokens(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAlgorithmNameTokens" ):
                return visitor.visitAlgorithmNameTokens(self)
            else:
                return visitor.visitChildren(self)




    def algorithmNameTokens(self):

        localctx = KumirParser.AlgorithmNameTokensContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_algorithmNameTokens)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 335 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 334
                    _la = self._input.LA(1)
                    if _la <= 0 or ((((_la - -1)) & ~0x3f) == 0 and ((1 << (_la - -1)) & 417) != 0) or _la==80 or _la==88:
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 337 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,29,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AlgorithmNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.ID)
            else:
                return self.getToken(KumirParser.ID, i)

        def getRuleIndex(self):
            return KumirParser.RULE_algorithmName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAlgorithmName" ):
                listener.enterAlgorithmName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAlgorithmName" ):
                listener.exitAlgorithmName(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAlgorithmName" ):
                return visitor.visitAlgorithmName(self)
            else:
                return visitor.visitChildren(self)




    def algorithmName(self):

        localctx = KumirParser.AlgorithmNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_algorithmName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 340 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 339
                    self.match(KumirParser.ID)

                else:
                    raise NoViableAltException(self)
                self.state = 342 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,30,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AlgorithmHeaderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALG_HEADER(self):
            return self.getToken(KumirParser.ALG_HEADER, 0)

        def algorithmNameTokens(self):
            return self.getTypedRuleContext(KumirParser.AlgorithmNameTokensContext,0)


        def typeSpecifier(self):
            return self.getTypedRuleContext(KumirParser.TypeSpecifierContext,0)


        def LPAREN(self):
            return self.getToken(KumirParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(KumirParser.RPAREN, 0)

        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def parameterList(self):
            return self.getTypedRuleContext(KumirParser.ParameterListContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_algorithmHeader

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAlgorithmHeader" ):
                listener.enterAlgorithmHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAlgorithmHeader" ):
                listener.exitAlgorithmHeader(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAlgorithmHeader" ):
                return visitor.visitAlgorithmHeader(self)
            else:
                return visitor.visitChildren(self)




    def algorithmHeader(self):

        localctx = KumirParser.AlgorithmHeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_algorithmHeader)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 344
            self.match(KumirParser.ALG_HEADER)
            self.state = 346
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,31,self._ctx)
            if la_ == 1:
                self.state = 345
                self.typeSpecifier()


            self.state = 348
            self.algorithmNameTokens()
            self.state = 354
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==80:
                self.state = 349
                self.match(KumirParser.LPAREN)
                self.state = 351
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 17996497085792256) != 0):
                    self.state = 350
                    self.parameterList()


                self.state = 353
                self.match(KumirParser.RPAREN)


            self.state = 357
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 356
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PreConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PRE_CONDITION(self):
            return self.getToken(KumirParser.PRE_CONDITION, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_preCondition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPreCondition" ):
                listener.enterPreCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPreCondition" ):
                listener.exitPreCondition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPreCondition" ):
                return visitor.visitPreCondition(self)
            else:
                return visitor.visitChildren(self)




    def preCondition(self):

        localctx = KumirParser.PreConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_preCondition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 359
            self.match(KumirParser.PRE_CONDITION)
            self.state = 360
            self.expression()
            self.state = 362
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 361
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PostConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def POST_CONDITION(self):
            return self.getToken(KumirParser.POST_CONDITION, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_postCondition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPostCondition" ):
                listener.enterPostCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPostCondition" ):
                listener.exitPostCondition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPostCondition" ):
                return visitor.visitPostCondition(self)
            else:
                return visitor.visitChildren(self)




    def postCondition(self):

        localctx = KumirParser.PostConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_postCondition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 364
            self.match(KumirParser.POST_CONDITION)
            self.state = 365
            self.expression()
            self.state = 367
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 366
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AlgorithmBodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statementSequence(self):
            return self.getTypedRuleContext(KumirParser.StatementSequenceContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_algorithmBody

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAlgorithmBody" ):
                listener.enterAlgorithmBody(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAlgorithmBody" ):
                listener.exitAlgorithmBody(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAlgorithmBody" ):
                return visitor.visitAlgorithmBody(self)
            else:
                return visitor.visitChildren(self)




    def algorithmBody(self):

        localctx = KumirParser.AlgorithmBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_algorithmBody)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 369
            self.statementSequence()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementSequenceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.StatementContext)
            else:
                return self.getTypedRuleContext(KumirParser.StatementContext,i)


        def getRuleIndex(self):
            return KumirParser.RULE_statementSequence

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatementSequence" ):
                listener.enterStatementSequence(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatementSequence" ):
                listener.exitStatementSequence(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatementSequence" ):
                return visitor.visitStatementSequence(self)
            else:
                return visitor.visitChildren(self)




    def statementSequence(self):

        localctx = KumirParser.StatementSequenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_statementSequence)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 374
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -17860605963520) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & 4178641287) != 0):
                self.state = 371
                self.statement()
                self.state = 376
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LvalueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def qualifiedIdentifier(self):
            return self.getTypedRuleContext(KumirParser.QualifiedIdentifierContext,0)


        def LBRACK(self):
            return self.getToken(KumirParser.LBRACK, 0)

        def indexList(self):
            return self.getTypedRuleContext(KumirParser.IndexListContext,0)


        def RBRACK(self):
            return self.getToken(KumirParser.RBRACK, 0)

        def RETURN_VALUE(self):
            return self.getToken(KumirParser.RETURN_VALUE, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_lvalue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLvalue" ):
                listener.enterLvalue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLvalue" ):
                listener.exitLvalue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLvalue" ):
                return visitor.visitLvalue(self)
            else:
                return visitor.visitChildren(self)




    def lvalue(self):

        localctx = KumirParser.LvalueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_lvalue)
        self._la = 0 # Token type
        try:
            self.state = 385
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [95]:
                self.enterOuterAlt(localctx, 1)
                self.state = 377
                self.qualifiedIdentifier()
                self.state = 382
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==82:
                    self.state = 378
                    self.match(KumirParser.LBRACK)
                    self.state = 379
                    self.indexList()
                    self.state = 380
                    self.match(KumirParser.RBRACK)


                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 2)
                self.state = 384
                self.match(KumirParser.RETURN_VALUE)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lvalue(self):
            return self.getTypedRuleContext(KumirParser.LvalueContext,0)


        def ASSIGN(self):
            return self.getToken(KumirParser.ASSIGN, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_assignmentStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignmentStatement" ):
                listener.enterAssignmentStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignmentStatement" ):
                listener.exitAssignmentStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssignmentStatement" ):
                return visitor.visitAssignmentStatement(self)
            else:
                return visitor.visitChildren(self)




    def assignmentStatement(self):

        localctx = KumirParser.AssignmentStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_assignmentStatement)
        try:
            self.state = 392
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,40,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 387
                self.lvalue()
                self.state = 388
                self.match(KumirParser.ASSIGN)
                self.state = 389
                self.expression()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 391
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IoArgumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.ExpressionContext,i)


        def COLON(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.COLON)
            else:
                return self.getToken(KumirParser.COLON, i)

        def NEWLINE_CONST(self):
            return self.getToken(KumirParser.NEWLINE_CONST, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_ioArgument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIoArgument" ):
                listener.enterIoArgument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIoArgument" ):
                listener.exitIoArgument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIoArgument" ):
                return visitor.visitIoArgument(self)
            else:
                return visitor.visitChildren(self)




    def ioArgument(self):

        localctx = KumirParser.IoArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_ioArgument)
        self._la = 0 # Token type
        try:
            self.state = 404
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,43,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 394
                self.expression()
                self.state = 401
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==87:
                    self.state = 395
                    self.match(KumirParser.COLON)
                    self.state = 396
                    self.expression()
                    self.state = 399
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==87:
                        self.state = 397
                        self.match(KumirParser.COLON)
                        self.state = 398
                        self.expression()




                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 403
                self.match(KumirParser.NEWLINE_CONST)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IoArgumentListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ioArgument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.IoArgumentContext)
            else:
                return self.getTypedRuleContext(KumirParser.IoArgumentContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(KumirParser.COMMA)
            else:
                return self.getToken(KumirParser.COMMA, i)

        def getRuleIndex(self):
            return KumirParser.RULE_ioArgumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIoArgumentList" ):
                listener.enterIoArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIoArgumentList" ):
                listener.exitIoArgumentList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIoArgumentList" ):
                return visitor.visitIoArgumentList(self)
            else:
                return visitor.visitChildren(self)




    def ioArgumentList(self):

        localctx = KumirParser.IoArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_ioArgumentList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 406
            self.ioArgument()
            self.state = 411
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==86:
                self.state = 407
                self.match(KumirParser.COMMA)
                self.state = 408
                self.ioArgument()
                self.state = 413
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IoStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INPUT(self):
            return self.getToken(KumirParser.INPUT, 0)

        def ioArgumentList(self):
            return self.getTypedRuleContext(KumirParser.IoArgumentListContext,0)


        def OUTPUT(self):
            return self.getToken(KumirParser.OUTPUT, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_ioStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIoStatement" ):
                listener.enterIoStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIoStatement" ):
                listener.exitIoStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIoStatement" ):
                return visitor.visitIoStatement(self)
            else:
                return visitor.visitChildren(self)




    def ioStatement(self):

        localctx = KumirParser.IoStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_ioStatement)
        try:
            self.state = 418
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [18]:
                self.enterOuterAlt(localctx, 1)
                self.state = 414
                self.match(KumirParser.INPUT)
                self.state = 415
                self.ioArgumentList()
                pass
            elif token in [19]:
                self.enterOuterAlt(localctx, 2)
                self.state = 416
                self.match(KumirParser.OUTPUT)
                self.state = 417
                self.ioArgumentList()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IfStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(KumirParser.IF, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def THEN(self):
            return self.getToken(KumirParser.THEN, 0)

        def statementSequence(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.StatementSequenceContext)
            else:
                return self.getTypedRuleContext(KumirParser.StatementSequenceContext,i)


        def FI(self):
            return self.getToken(KumirParser.FI, 0)

        def ELSE(self):
            return self.getToken(KumirParser.ELSE, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_ifStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIfStatement" ):
                listener.enterIfStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIfStatement" ):
                listener.exitIfStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfStatement" ):
                return visitor.visitIfStatement(self)
            else:
                return visitor.visitChildren(self)




    def ifStatement(self):

        localctx = KumirParser.IfStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_ifStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 420
            self.match(KumirParser.IF)
            self.state = 421
            self.expression()
            self.state = 422
            self.match(KumirParser.THEN)
            self.state = 423
            self.statementSequence()
            self.state = 426
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 424
                self.match(KumirParser.ELSE)
                self.state = 425
                self.statementSequence()


            self.state = 428
            self.match(KumirParser.FI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CaseBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CASE(self):
            return self.getToken(KumirParser.CASE, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def COLON(self):
            return self.getToken(KumirParser.COLON, 0)

        def statementSequence(self):
            return self.getTypedRuleContext(KumirParser.StatementSequenceContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_caseBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCaseBlock" ):
                listener.enterCaseBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCaseBlock" ):
                listener.exitCaseBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCaseBlock" ):
                return visitor.visitCaseBlock(self)
            else:
                return visitor.visitChildren(self)




    def caseBlock(self):

        localctx = KumirParser.CaseBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_caseBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 430
            self.match(KumirParser.CASE)
            self.state = 431
            self.expression()
            self.state = 432
            self.match(KumirParser.COLON)
            self.state = 433
            self.statementSequence()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SwitchStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SWITCH(self):
            return self.getToken(KumirParser.SWITCH, 0)

        def FI(self):
            return self.getToken(KumirParser.FI, 0)

        def caseBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.CaseBlockContext)
            else:
                return self.getTypedRuleContext(KumirParser.CaseBlockContext,i)


        def ELSE(self):
            return self.getToken(KumirParser.ELSE, 0)

        def statementSequence(self):
            return self.getTypedRuleContext(KumirParser.StatementSequenceContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_switchStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSwitchStatement" ):
                listener.enterSwitchStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSwitchStatement" ):
                listener.exitSwitchStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSwitchStatement" ):
                return visitor.visitSwitchStatement(self)
            else:
                return visitor.visitChildren(self)




    def switchStatement(self):

        localctx = KumirParser.SwitchStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_switchStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 435
            self.match(KumirParser.SWITCH)
            self.state = 437 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 436
                self.caseBlock()
                self.state = 439 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==17):
                    break

            self.state = 443
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 441
                self.match(KumirParser.ELSE)
                self.state = 442
                self.statementSequence()


            self.state = 445
            self.match(KumirParser.FI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EndLoopConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ENDLOOP_COND(self):
            return self.getToken(KumirParser.ENDLOOP_COND, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_endLoopCondition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEndLoopCondition" ):
                listener.enterEndLoopCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEndLoopCondition" ):
                listener.exitEndLoopCondition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEndLoopCondition" ):
                return visitor.visitEndLoopCondition(self)
            else:
                return visitor.visitChildren(self)




    def endLoopCondition(self):

        localctx = KumirParser.EndLoopConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_endLoopCondition)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 447
            self.match(KumirParser.ENDLOOP_COND)
            self.state = 448
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopSpecifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FOR(self):
            return self.getToken(KumirParser.FOR, 0)

        def ID(self):
            return self.getToken(KumirParser.ID, 0)

        def FROM(self):
            return self.getToken(KumirParser.FROM, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(KumirParser.ExpressionContext,i)


        def TO(self):
            return self.getToken(KumirParser.TO, 0)

        def STEP(self):
            return self.getToken(KumirParser.STEP, 0)

        def WHILE(self):
            return self.getToken(KumirParser.WHILE, 0)

        def TIMES(self):
            return self.getToken(KumirParser.TIMES, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_loopSpecifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLoopSpecifier" ):
                listener.enterLoopSpecifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLoopSpecifier" ):
                listener.exitLoopSpecifier(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoopSpecifier" ):
                return visitor.visitLoopSpecifier(self)
            else:
                return visitor.visitChildren(self)




    def loopSpecifier(self):

        localctx = KumirParser.LoopSpecifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_loopSpecifier)
        self._la = 0 # Token type
        try:
            self.state = 465
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [25]:
                self.enterOuterAlt(localctx, 1)
                self.state = 450
                self.match(KumirParser.FOR)
                self.state = 451
                self.match(KumirParser.ID)
                self.state = 452
                self.match(KumirParser.FROM)
                self.state = 453
                self.expression()
                self.state = 454
                self.match(KumirParser.TO)
                self.state = 455
                self.expression()
                self.state = 458
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==30:
                    self.state = 456
                    self.match(KumirParser.STEP)
                    self.state = 457
                    self.expression()


                pass
            elif token in [26]:
                self.enterOuterAlt(localctx, 2)
                self.state = 460
                self.match(KumirParser.WHILE)
                self.state = 461
                self.expression()
                pass
            elif token in [31, 32, 38, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 71, 72, 80, 84, 91, 92, 93, 94, 95]:
                self.enterOuterAlt(localctx, 3)
                self.state = 462
                self.expression()
                self.state = 463
                self.match(KumirParser.TIMES)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LOOP(self):
            return self.getToken(KumirParser.LOOP, 0)

        def statementSequence(self):
            return self.getTypedRuleContext(KumirParser.StatementSequenceContext,0)


        def ENDLOOP(self):
            return self.getToken(KumirParser.ENDLOOP, 0)

        def endLoopCondition(self):
            return self.getTypedRuleContext(KumirParser.EndLoopConditionContext,0)


        def loopSpecifier(self):
            return self.getTypedRuleContext(KumirParser.LoopSpecifierContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_loopStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLoopStatement" ):
                listener.enterLoopStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLoopStatement" ):
                listener.exitLoopStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoopStatement" ):
                return visitor.visitLoopStatement(self)
            else:
                return visitor.visitChildren(self)




    def loopStatement(self):

        localctx = KumirParser.LoopStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_loopStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 467
            self.match(KumirParser.LOOP)
            self.state = 469
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,51,self._ctx)
            if la_ == 1:
                self.state = 468
                self.loopSpecifier()


            self.state = 471
            self.statementSequence()
            self.state = 474
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [11]:
                self.state = 472
                self.match(KumirParser.ENDLOOP)
                pass
            elif token in [10]:
                self.state = 473
                self.endLoopCondition()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExitStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXIT(self):
            return self.getToken(KumirParser.EXIT, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_exitStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExitStatement" ):
                listener.enterExitStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExitStatement" ):
                listener.exitExitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExitStatement" ):
                return visitor.visitExitStatement(self)
            else:
                return visitor.visitChildren(self)




    def exitStatement(self):

        localctx = KumirParser.ExitStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_exitStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 476
            self.match(KumirParser.EXIT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PauseStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PAUSE(self):
            return self.getToken(KumirParser.PAUSE, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_pauseStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPauseStatement" ):
                listener.enterPauseStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPauseStatement" ):
                listener.exitPauseStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPauseStatement" ):
                return visitor.visitPauseStatement(self)
            else:
                return visitor.visitChildren(self)




    def pauseStatement(self):

        localctx = KumirParser.PauseStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 98, self.RULE_pauseStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 478
            self.match(KumirParser.PAUSE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StopStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STOP(self):
            return self.getToken(KumirParser.STOP, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_stopStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStopStatement" ):
                listener.enterStopStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStopStatement" ):
                listener.exitStopStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStopStatement" ):
                return visitor.visitStopStatement(self)
            else:
                return visitor.visitChildren(self)




    def stopStatement(self):

        localctx = KumirParser.StopStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 100, self.RULE_stopStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 480
            self.match(KumirParser.STOP)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssertionStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSERTION(self):
            return self.getToken(KumirParser.ASSERTION, 0)

        def expression(self):
            return self.getTypedRuleContext(KumirParser.ExpressionContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_assertionStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssertionStatement" ):
                listener.enterAssertionStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssertionStatement" ):
                listener.exitAssertionStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssertionStatement" ):
                return visitor.visitAssertionStatement(self)
            else:
                return visitor.visitChildren(self)




    def assertionStatement(self):

        localctx = KumirParser.AssertionStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 102, self.RULE_assertionStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 482
            self.match(KumirParser.ASSERTION)
            self.state = 483
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProcedureCallStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def qualifiedIdentifier(self):
            return self.getTypedRuleContext(KumirParser.QualifiedIdentifierContext,0)


        def LPAREN(self):
            return self.getToken(KumirParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(KumirParser.RPAREN, 0)

        def argumentList(self):
            return self.getTypedRuleContext(KumirParser.ArgumentListContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_procedureCallStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProcedureCallStatement" ):
                listener.enterProcedureCallStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProcedureCallStatement" ):
                listener.exitProcedureCallStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProcedureCallStatement" ):
                return visitor.visitProcedureCallStatement(self)
            else:
                return visitor.visitChildren(self)




    def procedureCallStatement(self):

        localctx = KumirParser.ProcedureCallStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 104, self.RULE_procedureCallStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 485
            self.qualifiedIdentifier()
            self.state = 491
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,54,self._ctx)
            if la_ == 1:
                self.state = 486
                self.match(KumirParser.LPAREN)
                self.state = 488
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & -18014117189124096) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & 4161864071) != 0):
                    self.state = 487
                    self.argumentList()


                self.state = 490
                self.match(KumirParser.RPAREN)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variableDeclaration(self):
            return self.getTypedRuleContext(KumirParser.VariableDeclarationContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def assignmentStatement(self):
            return self.getTypedRuleContext(KumirParser.AssignmentStatementContext,0)


        def ioStatement(self):
            return self.getTypedRuleContext(KumirParser.IoStatementContext,0)


        def ifStatement(self):
            return self.getTypedRuleContext(KumirParser.IfStatementContext,0)


        def switchStatement(self):
            return self.getTypedRuleContext(KumirParser.SwitchStatementContext,0)


        def loopStatement(self):
            return self.getTypedRuleContext(KumirParser.LoopStatementContext,0)


        def exitStatement(self):
            return self.getTypedRuleContext(KumirParser.ExitStatementContext,0)


        def pauseStatement(self):
            return self.getTypedRuleContext(KumirParser.PauseStatementContext,0)


        def stopStatement(self):
            return self.getTypedRuleContext(KumirParser.StopStatementContext,0)


        def assertionStatement(self):
            return self.getTypedRuleContext(KumirParser.AssertionStatementContext,0)


        def procedureCallStatement(self):
            return self.getTypedRuleContext(KumirParser.ProcedureCallStatementContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = KumirParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 106, self.RULE_statement)
        try:
            self.state = 538
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,66,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 493
                self.variableDeclaration()
                self.state = 495
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,55,self._ctx)
                if la_ == 1:
                    self.state = 494
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 497
                self.assignmentStatement()
                self.state = 499
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,56,self._ctx)
                if la_ == 1:
                    self.state = 498
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 501
                self.ioStatement()
                self.state = 503
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,57,self._ctx)
                if la_ == 1:
                    self.state = 502
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 505
                self.ifStatement()
                self.state = 507
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,58,self._ctx)
                if la_ == 1:
                    self.state = 506
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 509
                self.switchStatement()
                self.state = 511
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,59,self._ctx)
                if la_ == 1:
                    self.state = 510
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 513
                self.loopStatement()
                self.state = 515
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,60,self._ctx)
                if la_ == 1:
                    self.state = 514
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 517
                self.exitStatement()
                self.state = 519
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,61,self._ctx)
                if la_ == 1:
                    self.state = 518
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 521
                self.pauseStatement()
                self.state = 523
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,62,self._ctx)
                if la_ == 1:
                    self.state = 522
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 525
                self.stopStatement()
                self.state = 527
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,63,self._ctx)
                if la_ == 1:
                    self.state = 526
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 529
                self.assertionStatement()
                self.state = 531
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,64,self._ctx)
                if la_ == 1:
                    self.state = 530
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 533
                self.procedureCallStatement()
                self.state = 535
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,65,self._ctx)
                if la_ == 1:
                    self.state = 534
                    self.match(KumirParser.SEMICOLON)


                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 537
                self.match(KumirParser.SEMICOLON)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AlgorithmDefinitionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def algorithmHeader(self):
            return self.getTypedRuleContext(KumirParser.AlgorithmHeaderContext,0)


        def ALG_BEGIN(self):
            return self.getToken(KumirParser.ALG_BEGIN, 0)

        def algorithmBody(self):
            return self.getTypedRuleContext(KumirParser.AlgorithmBodyContext,0)


        def ALG_END(self):
            return self.getToken(KumirParser.ALG_END, 0)

        def preCondition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.PreConditionContext)
            else:
                return self.getTypedRuleContext(KumirParser.PreConditionContext,i)


        def postCondition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.PostConditionContext)
            else:
                return self.getTypedRuleContext(KumirParser.PostConditionContext,i)


        def variableDeclaration(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.VariableDeclarationContext)
            else:
                return self.getTypedRuleContext(KumirParser.VariableDeclarationContext,i)


        def algorithmName(self):
            return self.getTypedRuleContext(KumirParser.AlgorithmNameContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_algorithmDefinition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAlgorithmDefinition" ):
                listener.enterAlgorithmDefinition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAlgorithmDefinition" ):
                listener.exitAlgorithmDefinition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAlgorithmDefinition" ):
                return visitor.visitAlgorithmDefinition(self)
            else:
                return visitor.visitChildren(self)




    def algorithmDefinition(self):

        localctx = KumirParser.AlgorithmDefinitionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 108, self.RULE_algorithmDefinition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 540
            self.algorithmHeader()
            self.state = 546
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 17996256567623872) != 0):
                self.state = 544
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [6]:
                    self.state = 541
                    self.preCondition()
                    pass
                elif token in [7]:
                    self.state = 542
                    self.postCondition()
                    pass
                elif token in [39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53]:
                    self.state = 543
                    self.variableDeclaration()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 548
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 549
            self.match(KumirParser.ALG_BEGIN)
            self.state = 550
            self.algorithmBody()
            self.state = 551
            self.match(KumirParser.ALG_END)
            self.state = 553
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,69,self._ctx)
            if la_ == 1:
                self.state = 552
                self.algorithmName()


            self.state = 556
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,70,self._ctx)
            if la_ == 1:
                self.state = 555
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ModuleNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def qualifiedIdentifier(self):
            return self.getTypedRuleContext(KumirParser.QualifiedIdentifierContext,0)


        def STRING(self):
            return self.getToken(KumirParser.STRING, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_moduleName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterModuleName" ):
                listener.enterModuleName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitModuleName" ):
                listener.exitModuleName(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitModuleName" ):
                return visitor.visitModuleName(self)
            else:
                return visitor.visitChildren(self)




    def moduleName(self):

        localctx = KumirParser.ModuleNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 110, self.RULE_moduleName)
        try:
            self.state = 560
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [95]:
                self.enterOuterAlt(localctx, 1)
                self.state = 558
                self.qualifiedIdentifier()
                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 2)
                self.state = 559
                self.match(KumirParser.STRING)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ImportStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IMPORT(self):
            return self.getToken(KumirParser.IMPORT, 0)

        def moduleName(self):
            return self.getTypedRuleContext(KumirParser.ModuleNameContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_importStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterImportStatement" ):
                listener.enterImportStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitImportStatement" ):
                listener.exitImportStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitImportStatement" ):
                return visitor.visitImportStatement(self)
            else:
                return visitor.visitChildren(self)




    def importStatement(self):

        localctx = KumirParser.ImportStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 112, self.RULE_importStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 562
            self.match(KumirParser.IMPORT)
            self.state = 563
            self.moduleName()
            self.state = 565
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,72,self._ctx)
            if la_ == 1:
                self.state = 564
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProgramItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def importStatement(self):
            return self.getTypedRuleContext(KumirParser.ImportStatementContext,0)


        def globalDeclaration(self):
            return self.getTypedRuleContext(KumirParser.GlobalDeclarationContext,0)


        def globalAssignment(self):
            return self.getTypedRuleContext(KumirParser.GlobalAssignmentContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_programItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgramItem" ):
                listener.enterProgramItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgramItem" ):
                listener.exitProgramItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgramItem" ):
                return visitor.visitProgramItem(self)
            else:
                return visitor.visitChildren(self)




    def programItem(self):

        localctx = KumirParser.ProgramItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 114, self.RULE_programItem)
        try:
            self.state = 570
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [24]:
                self.enterOuterAlt(localctx, 1)
                self.state = 567
                self.importStatement()
                pass
            elif token in [39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53]:
                self.enterOuterAlt(localctx, 2)
                self.state = 568
                self.globalDeclaration()
                pass
            elif token in [95]:
                self.enterOuterAlt(localctx, 3)
                self.state = 569
                self.globalAssignment()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ModuleHeaderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MODULE(self):
            return self.getToken(KumirParser.MODULE, 0)

        def qualifiedIdentifier(self):
            return self.getTypedRuleContext(KumirParser.QualifiedIdentifierContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_moduleHeader

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterModuleHeader" ):
                listener.enterModuleHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitModuleHeader" ):
                listener.exitModuleHeader(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitModuleHeader" ):
                return visitor.visitModuleHeader(self)
            else:
                return visitor.visitChildren(self)




    def moduleHeader(self):

        localctx = KumirParser.ModuleHeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 116, self.RULE_moduleHeader)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 572
            self.match(KumirParser.MODULE)
            self.state = 573
            self.qualifiedIdentifier()
            self.state = 575
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 574
                self.match(KumirParser.SEMICOLON)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ModuleBodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def programItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ProgramItemContext)
            else:
                return self.getTypedRuleContext(KumirParser.ProgramItemContext,i)


        def algorithmDefinition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.AlgorithmDefinitionContext)
            else:
                return self.getTypedRuleContext(KumirParser.AlgorithmDefinitionContext,i)


        def getRuleIndex(self):
            return KumirParser.RULE_moduleBody

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterModuleBody" ):
                listener.enterModuleBody(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitModuleBody" ):
                listener.exitModuleBody(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitModuleBody" ):
                return visitor.visitModuleBody(self)
            else:
                return visitor.visitChildren(self)




    def moduleBody(self):

        localctx = KumirParser.ModuleBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 118, self.RULE_moduleBody)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 581
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 17996256584400904) != 0) or _la==95:
                self.state = 579
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [24, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53, 95]:
                    self.state = 577
                    self.programItem()
                    pass
                elif token in [3]:
                    self.state = 578
                    self.algorithmDefinition()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 583
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ImplicitModuleBodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def programItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ProgramItemContext)
            else:
                return self.getTypedRuleContext(KumirParser.ProgramItemContext,i)


        def algorithmDefinition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.AlgorithmDefinitionContext)
            else:
                return self.getTypedRuleContext(KumirParser.AlgorithmDefinitionContext,i)


        def getRuleIndex(self):
            return KumirParser.RULE_implicitModuleBody

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterImplicitModuleBody" ):
                listener.enterImplicitModuleBody(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitImplicitModuleBody" ):
                listener.exitImplicitModuleBody(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitImplicitModuleBody" ):
                return visitor.visitImplicitModuleBody(self)
            else:
                return visitor.visitChildren(self)




    def implicitModuleBody(self):

        localctx = KumirParser.ImplicitModuleBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 120, self.RULE_implicitModuleBody)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 586 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 586
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [24, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53, 95]:
                        self.state = 584
                        self.programItem()
                        pass
                    elif token in [3]:
                        self.state = 585
                        self.algorithmDefinition()
                        pass
                    else:
                        raise NoViableAltException(self)


                else:
                    raise NoViableAltException(self)
                self.state = 588 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,78,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ModuleDefinitionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def moduleHeader(self):
            return self.getTypedRuleContext(KumirParser.ModuleHeaderContext,0)


        def moduleBody(self):
            return self.getTypedRuleContext(KumirParser.ModuleBodyContext,0)


        def ENDMODULE(self):
            return self.getToken(KumirParser.ENDMODULE, 0)

        def qualifiedIdentifier(self):
            return self.getTypedRuleContext(KumirParser.QualifiedIdentifierContext,0)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def implicitModuleBody(self):
            return self.getTypedRuleContext(KumirParser.ImplicitModuleBodyContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_moduleDefinition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterModuleDefinition" ):
                listener.enterModuleDefinition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitModuleDefinition" ):
                listener.exitModuleDefinition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitModuleDefinition" ):
                return visitor.visitModuleDefinition(self)
            else:
                return visitor.visitChildren(self)




    def moduleDefinition(self):

        localctx = KumirParser.ModuleDefinitionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 122, self.RULE_moduleDefinition)
        try:
            self.state = 600
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 590
                self.moduleHeader()
                self.state = 591
                self.moduleBody()
                self.state = 592
                self.match(KumirParser.ENDMODULE)
                self.state = 594
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,79,self._ctx)
                if la_ == 1:
                    self.state = 593
                    self.qualifiedIdentifier()


                self.state = 597
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,80,self._ctx)
                if la_ == 1:
                    self.state = 596
                    self.match(KumirParser.SEMICOLON)


                pass
            elif token in [3, 24, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53, 95]:
                self.enterOuterAlt(localctx, 2)
                self.state = 599
                self.implicitModuleBody()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(KumirParser.EOF, 0)

        def programItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ProgramItemContext)
            else:
                return self.getTypedRuleContext(KumirParser.ProgramItemContext,i)


        def moduleDefinition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.ModuleDefinitionContext)
            else:
                return self.getTypedRuleContext(KumirParser.ModuleDefinitionContext,i)


        def algorithmDefinition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(KumirParser.AlgorithmDefinitionContext)
            else:
                return self.getTypedRuleContext(KumirParser.AlgorithmDefinitionContext,i)


        def SEMICOLON(self):
            return self.getToken(KumirParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgram" ):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)




    def program(self):

        localctx = KumirParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 124, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 605
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,82,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 602
                    self.programItem() 
                self.state = 607
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,82,self._ctx)

            self.state = 612
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 17996256584400906) != 0) or _la==95:
                self.state = 610
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,83,self._ctx)
                if la_ == 1:
                    self.state = 608
                    self.moduleDefinition()
                    pass

                elif la_ == 2:
                    self.state = 609
                    self.algorithmDefinition()
                    pass


                self.state = 614
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 616
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 615
                self.match(KumirParser.SEMICOLON)


            self.state = 618
            self.match(KumirParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





