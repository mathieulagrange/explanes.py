import explanes as el
import numpy as np
import pandas as pd

experiment = el.experiment.Experiment()
experiment.project.name = 'example'
experiment.path.output = '/tmp/'+experiment.project.name+'/'
experiment.factor.f1 = [1, 2]
experiment.factor.f2 = [1, 2, 3]
experiment.metric.m1 = ['mean', 'std']
experiment.metric.m2 = ['min', 'argmin']

def process(setting, experiment):
  metric1 = setting.f1+setting.f2+np.random.randn(100)
  metric2 = setting.f1*setting.f2*np.random.randn(100)
  np.save(experiment.path.output+setting.id()+'_m1.npy', metric1)
  np.save(experiment.path.output+setting.id()+'_m2.npy', metric2)

experiment.setPath()
experiment.do([], process, progress=False)

(settingMetric, settingDescription, constantSettingDescription) = experiment.metric.get('m1', experiment.factor.mask([1]), experiment.path.output)

print(constantSettingDescription)
print(settingDescription)
print(len(settingMetric))
print(settingMetric[0].shape)
