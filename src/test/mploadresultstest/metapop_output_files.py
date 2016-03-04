import re
import string

directory = r'C:\afat32\Dropbox\GlobalEcologyGroup\ProjectCode\LatinHypercubeSensitivityTool\v2.0\Test\MpResultExtractionTest\\'
metapop_output_files = ['Abund.txt', 'FinalStageN.txt', 'Harvest.txt', 'HarvestRisk.txt', 'IntExpRisk.txt', 'IntExtRisk.txt', 'IntPerDec.txt', 'LocalOcc.txt', 'LocExtDur.txt', 'MetapopOcc.txt', 'QuasiExp.txt', 'QuasiExt.txt', 'TerExpRisk.txt', 'TerExtRisk.txt', 'TerPerDec.txt']

for ouput_file in metapop_output_files :
    
    f = open(directory + ouput_file)
    lines = f.readlines()
    f.close()
    modified_lines = []
    for line in lines :
        line = re.sub('^ +', '', line)
        line = string.join(re.split('   +', line), '\t')
        line = string.replace(line, 'Minimum', '\tMinimum')
        line = re.sub('^5th', '\t5th', line)
        modified_lines.append(line)   

    f = open(directory + ouput_file, 'w')
    f.write(string.join(modified_lines, ''))
    f.close()
