
# coding: utf-8

# In[1]:

from os import listdir
from os import path
import os
import numpy as np
import csv
import combine2python
#import ipythonify
import sys
from IPython.display import clear_output
import tellurium as te

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

root_path = path.abspath('C:/Users/Kiri Choi/projects/sbmltest2archive/sbml-test-cases/cases/semantic/')
cases = [case for case in listdir(root_path) if is_number(case)]
cases = sorted(cases)


# In[ ]:

threshold = 5

report = ['Running test suite with sum square residual threshold of %f' % threshold]
num_cases = 0
num_passed = 0
#a = ["00007", "00008"]

for case in cases:
    print str(case)
    with open('case.log', 'wb') as f:
        f.write(case)
    folder_path = path.join(root_path, case)
    ls = listdir(folder_path)
    
    if 'manifest.xml' not in ls:
        continue
        
    if case == '00999':
        continue
    
    if int(case) > int(1085):
        continue
    
    try:
        num_cases += 1
        
        sbmlfname, sedmlfname = combine2python.manifestsearch(folder_path)
#         sbml = [file for file in sorted(ls) if 'sbml-l2v4.xml' in file][0]
        with open(path.join(folder_path, '.' + sbmlfname), 'rb') as f:
            sbml = f.read()
        rr = te.loada(te.sbmlToAntimony(sbml))
        rr.simulate()
        
        combine2python.codestitch('test' + str(case) + '.py', folder_path, case)
        combine2python.codeanalysis('test' + str(case) + '.py', folder_path)
        pyscriptname = 'test' + str(case)
        test = __import__(pyscriptname)
        num_timepoints = len(test.allX_0)
        results_file = [file for file in ls if 'results.csv' in file][0]
        computed_result = np.hstack([test.allX_0[:,0].reshape(num_timepoints, 1), test.allY_0])
                
        with open(os.path.join(folder_path, results_file), 'rb') as f:
            reader = csv.reader(f)
            rows = []
            for i, row in enumerate(reader):
                if i == 0:
                    header = row
                else:
                    rows.append([float(item) for item in row])
        expected_result = np.array(rows)
        ssr = sum(sum((computed_result - expected_result)**2))
        print ssr
        if ssr > threshold:
            report.append('%s: FAILED... with SSR of %f' % (case, ssr))
        else:
            num_passed += 1
            report.append('%s: PASSED' % case)
    except:
        report.append('%s: FAILED... ERROR: %s' % (case,  sys.exc_info()[1]))
    try:
        os.remove(pyscriptname + '.py')
        os.remove(pyscriptname + '.pyc')
    except:
        pass
    clear_output()

report.append('Total Cases: %d' % num_cases)
report.append('Total Passed: %d' % num_passed)
report.append('Total Failed: %d' % (num_cases-num_passed,))
#print '\n'.join(report)


# In[ ]:

with open('report.log', 'wb') as f:
    f.write('\n'.join(report))


# In[14]:

#print '\n'.join(report)

