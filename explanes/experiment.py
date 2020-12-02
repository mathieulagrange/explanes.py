import smtplib
import types
import inspect
import os
import time
import datetime
import explanes as el
import sys
import pandas as pd
import argparse
import argunparse
import ast
import importlib
import os
import copy

def run():
  """This method shall be called from the main script of the experiment to control the experiment using the command line.

  This method provides a front-end for running an explanes experiment. It should be called from the main script of the experiment. The main script must define a **set** function that will be called before processing and a **step** function that will be processed for each setting. It may also define a **display** function that will used to monitor the results.

  Examples

  Assuming that the file experiment_run.py contains:

  >>> import explanes as el
  >>> if __name__ == "__main__":
  ...   el.experiment.run() # doctest: +SKIP
  >>> def set(experiment, args):
  ...   experiment.factor.factor1=[1, 3]
  ...   experiment.factor.factor2=[2, 4]
  ...   return experiment
  >>> def step(setting, experiment):
  ...   print(setting.id())

  Executing this file with the --run option gives::

  $ python experiment_run.py -r
   factor1_1_factor2_2
   factor1_1_factor2_4
   factor1_3_factor2_2
   factor1_3_factor2_4

  Executing this file with the --help option gives::

  $ python experiment_run.py -h

  usage: experiment_run.py [-h] [-i] [-f] [-l] [-m MASK] [-M [MAIL]] [-C] [-S]
                         [-s SERVER] [-d [DISPLAY]] [-r [RUN]] [-D] [-v] [-P]
                         [-R [REMOVE]] [-K [KEEP]]

optional arguments:
  -h, --help            show this help message and exit
  -i, --information     show information about the experiment
  -f, --factor          show the factors of the experiment
  -l, --list            list settings
  -m MASK, --mask MASK  mask of the experiment to run
  -M [MAIL], --mail [MAIL]
                        send email at the beginning and end of the
                        computation. If a positive integer value x is
                        provided, additional emails are sent every x hours.
  -C, --copy            copy codebase to server defined by -s argument
  -S, --serverDefault   augment the command line with the content of the dict
                        experiment._defaultServerRunArgument
  -s SERVER, --server SERVER
                        running server side. Integer defines the index in the
                        host array of config. -2 (default) runs attached on
                        the local host, -1 runs detached on the local host, -3
                        is a flag meaning that the experiment runs serverside
  -d [DISPLAY], --display [DISPLAY]
                        display metrics. Str parameter (optional) should
                        contain a list of integers specifiying the columns to
                        keep for display.
  -r [RUN], --run [RUN]
                        perform computation. Integer parameter sets the number
                        of jobs computed in parallel (default to one core).
  -D, --debug           debug mode
  -v, --version         print version
  -P, --progress        display progress bar
  -R [REMOVE], --remove [REMOVE]
                        remove the selected settings from a given path (all
                        paths of the experiment by default, if the argument
                        does not have / or \, the argument is interpreted as a
                        member of the experiments path)
  -K [KEEP], --keep [KEEP]
                        keep only the selected settings from a given path (all
                        paths of the experiment by default, if the argument
                        does not have / or \, the argument is interpreted as a
                        member of the experiments path)

  """

  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--information', help='show information about the experiment', action='store_true')
  parser.add_argument('-f', '--factor', help='show the factors of the experiment', action='store_true')
  parser.add_argument('-l', '--list', help='list settings', action='store_true')
  parser.add_argument('-m', '--mask', type=str, help='mask of the experiment to run', default='[]')
  parser.add_argument('-M', '--mail', help='send email at the beginning and end of the computation. If a positive integer value x is provided, additional emails are sent every x hours.', nargs='?', default='-1')
  parser.add_argument('-C', '--copy', help='copy codebase to server defined by -s argument', action='store_true')
  parser.add_argument('-S', '--serverDefault', help='augment the command line with the content of the dict experiment._defaultServerRunArgument', action='store_true')
  parser.add_argument('-s', '--server', type=int, help='running server side. Integer defines the index in the host array of config. -2 (default) runs attached on the local host, -1 runs detached on the local host, -3 is a flag meaning that the experiment runs serverside', default=-2)
  parser.add_argument('-d', '--display', type=str, help='display metrics. Str parameter (optional) should contain a list of integers specifiying the columns to keep for display.', nargs='?', default='-1')
  parser.add_argument('-r', '--run', type=int, help='perform computation. Integer parameter sets the number of jobs computed in parallel (default to one core).', nargs='?', const=1)
  parser.add_argument('-D', '--debug', help='debug mode', action='store_true')
  parser.add_argument('-v', '--version', help='print version', action='store_true')
  parser.add_argument('-P', '--progress', help='display progress bar', action='store_true')
  parser.add_argument('-R', '--remove', type=str, help='remove the selected  settings from a given path (all paths of the experiment by default, if the argument does not have / or \, the argument is interpreted as a member of the experiments path)', nargs='?', const='all')
  parser.add_argument('-K', '--keep', type=str, help='keep only the selected settings from a given path (all paths of the experiment by default, if the argument does not have / or \, the argument is interpreted as a member of the experiments path)', nargs='?', const='all')

  args = parser.parse_args()



  if args.version:
    print("Experiment version "+experiment.project.version)
    exit(1)
  if args.mail is None:
    args.mail = 0
  else:
    args.mail = float(args.mail)

  mask = ast.literal_eval(args.mask)
  selectDisplay = []
  display = True
  if args.display == '-1':
    display = False
  elif args.display is None:
    args.display = '-2'
  elif args.display == '-2':
    selectDisplay = ast.literal_eval(args.display)

  module = sys.argv[0][:-3]
  try:
    config = importlib.import_module(module)
  except:
   print('Please provide a valid project name')
   raise ValueError
  experiment = config.set(args)
  if args.serverDefault:
    args.serverDefault = False
    for key in experiment._defaultServerRunArgument:
      # args[key] =
      args.__setattr__(key, experiment._defaultServerRunArgument[key])

  if args.information:
      print(experiment)
  if args.factor:
      print(experiment.factor.asPandaFrame())
  if args.list:
    experiment.do(mask, progress=False)

  if args.remove:
    path2clean = args.remove
    if path2clean == 'all':
      experiment.clean(mask, settingEncoding=experiment._settingEncoding)
    else:
      experiment.cleanDataSink(path2clean, mask, settingEncoding=experiment._settingEncoding)

  if args.keep:
    path2clean = args.keep
    if path2clean == 'all':
      experiment.clean(mask, reverse=True, settingEncoding=experiment._settingEncoding)
    else:
      experiment.cleanDataSink(path2clean, mask, reverse=True, settingEncoding=experiment._settingEncoding)

  logFileName = ''
  if args.server>-2:
    unparser = argunparse.ArgumentUnparser()
    kwargs = copy.deepcopy(vars(args))
    kwargs['server'] = -3
    command = unparser.unparse(**kwargs).replace('\'', '\"').replace('\"', '\\\"')
    if args.debug:
      command += '; bash '
    command = 'screen -dm bash -c \'python3 '+experiment.project.name+'.py '+command+'\''
    message = 'experiment launched on local host'
    if args.server>-1:
      if args.copy:
        syncCommand = 'rsync -r '+experiment.path.code+'/* '+experiment.host[args.server]+':'+experiment.path.code
        print(syncCommand)
        os.system(syncCommand)
      command = 'ssh '+experiment.host[args.server]+' "cd '+experiment.path.code+'; '+command+'"'
      message = 'experiment launched on host: '+experiment.host[args.server]
    print(command)
    os.system(command)
    print(message)
    exit()

  if args.server == -3:
    logFileName = '/tmp/explanes_'+experiment.project.name+'_'+experiment.project.runId+'.txt'
  if args.mail>-1:
    experiment.sendMail(args.mask+' has started.', '<div> Mask = '+args.mask+'</div>')
  if args.run and hasattr(config, 'step'):
    experiment.do(mask, config.step, nbJobs=args.run, logFileName=logFileName, progress=args.progress, mailInterval = float(args.mail))

  body = '<div> Mask = '+args.mask+'</div>'
  if display:
    if hasattr(config, 'display'):
      config.display(experiment, experiment.factor.mask(mask))
    else:
      (table, columns, header, nbFactorColumns) = experiment.metric.reduce(experiment.factor.mask(mask), experiment.path.output, factorDisplay=experiment._factorFormatInReduce, settingEncoding = experiment._settingEncoding, verbose=args.debug, reductionDirectiveModule=config)
      # print(table)
      # print(columns)
      df = pd.DataFrame(table, columns=columns).fillna('')
      df[columns[nbFactorColumns:]] = df[columns[nbFactorColumns:]].round(decimals=2)
      if selectDisplay:
        selector = [columns[i] for i in selectDisplay]
        df = df[selector]
      print(header)
      print(df)
      body += '<div> '+header+' </div><br>'+df.to_html()
  if args.server == -3:
    logFileName = '/tmp/explanes_'+experiment.project.name+'_'+experiment.project.runId+'.txt'
    with open(logFileName, 'r') as file:
      log = file.read()
      if log:
        body+= '<h2> Error log </h2>'+log.replace('\n', '<br>')

  if args.mail>-1:
    experiment.sendMail(args.mask+' is over.', body) #


class Experiment():
  """Stores high level information about the experiment and tools to control the processing and storage of data.

  The experiment class displays high level information about the experiment in the experiment.project NameSpace such as its name, description, author, author's email address, and run identification. Information about storage of data is specified using the experiment.path NameSpace. It also stores a Factor object and a Metric object to respectively specify the factors and the metrics considered in the experiment.

  See Also
  --------

  explanes.factor.Factor, explanes.metric.Metric

  Examples
  --------

  >>> import explanes as el
  >>> e=el.experiment.Experiment()
  >>> e.project.name='myExperiment'
  >>> e.project.author='Mathieu Lagrange'
  >>> e.project.address='mathieu.lagrange@ls2n.fr'
  >>> e.path.processing='/tmp'
  >>> print(e)
  project:
    name: myExperiment
    description:
    author: Mathieu Lagrange
    address: mathieu.lagrange@ls2n.fr
    runId: ...
  factor:
  parameter:
  metric:
  path:
    input:
    processing: /tmp
    storage:
    output:
  host: []

  Each level can be complemented with new members to store specific information:

  >>> e.specificInfo = 'stuff'
  >>> import types
  >>> e.myData = types.SimpleNamespace()
  >>> e.myData.info1= 1
  >>> e.myData.info2= 2
  >>> print(e)
   project:
    name: myExperiment
    description:
    author: Mathieu Lagrange
    address: mathieu.lagrange@ls2n.fr
    runId: ...
  factor:
  parameter:
  metric:
  path:
    input:
    processing: /tmp
    storage:
    output:
  host: []
  specificInfo: stuff
  myData:
    info1: 1
    info2: 2

  """

  def __init__(
    self
    ):
    # list of attributes (preserving order of insertion for antique versions of python)
    self._atrs = []
    self.project = types.SimpleNamespace()
    self.project.name = ''
    self.project.description = ''
    self.project.author = 'no name'
    self.project.address = 'noname@noorg.org'
    self.project.runId = str(int((time.time()-datetime.datetime(2020,1,1,0,0).timestamp())/60))
    self.factor = el.Factor()
    self.parameter = types.SimpleNamespace()
    self.metric = el.Metric()
    self.path = Path()
    self.path.input = ''
    self.path.processing = ''
    self.path.storage = ''
    self.path.output = ''
    self.host = []
    self._settingEncoding = {}
    self._archivePath = ''
    self._factorFormatInReduce = 'long'
    self._gmailId = 'expcode.mailer'
    self._gmailAppPassword = 'tagsqtlirkznoxro'
    self._defaultServerRunArgument =  {}

  def __setattr__(
    self,
    name,
    value
    ):
    if not hasattr(self, name) and name[0] != '_':
      self._atrs.append(name)
    return object.__setattr__(self, name, value)

  # def expandPath(
  #   self
  #   ):
  #   """
  #
  #   Examples
  #   --------
  #
  #   >>> import explanes as el
  #   >>> import os
  #   >>> e=el.Experiment()
  #   >>> e.project.name = 'experiment'
  #   >>> e.path.processing = '/tmp/'+e.project.name+'/processing'
  #   >>> e.path.output = '/tmp/'+e.project.name+'/output'
  #   >>> e.setPath(force=True)
  #   >>> os.listdir('/tmp/'+e.project.name)
  #   ['processing', 'output']
  #   """
  #   for sns in self.__getattribute__('path').__dict__.keys():
  #     self.__getattribute__('path') = os.path.abspath(os.path.expanduser(self.__getattribute__('path').__getattribute__(sns)))

  def setPath(
    self,
    force=False
    ):
    """Create directories whose path described in experiment.path are not reachable.

    For each path set in experiment.path, create the directory if not reachable. The user may be prompted before creation.

  	Parameters
  	----------

    force : bool
      If True, do not prompt the user before creating the missing directories.

      If False, prompt the user before creation of each missing directory.

    Examples
    --------

    >>> import explanes as el
    >>> import os
    >>> e=el.Experiment()
    >>> e.project.name = 'experiment'
    >>> e.path.processing = '/tmp/'+e.project.name+'/processing'
    >>> e.path.output = '/tmp/'+e.project.name+'/output'
    >>> e.setPath(force=True)
    >>> os.listdir('/tmp/'+e.project.name)
    ['processing', 'output']
    """
    for sns in self.__getattribute__('path').__dict__.keys():
      path = os.path.abspath(os.path.expanduser(self.__getattribute__('path').__getattribute__(sns)))
      if path:
        if path.endswith('.h5'):
          path = os.path.dirname(os.path.abspath(path))
        if not os.path.exists(path):
          if force or el.util.query_yes_no('The '+sns+' path: '+path+' does not exist. Do you want to create it ?'):
            os.makedirs(path)
            if not force:
              print('Path succesfully created.')

  def __str__(
    self,
    format='str'
    ):
    """Provide a textual description of the experiment

    List all members of the class and theirs values

    parameters
    ----------
    format : str
      If 'str', return the description as a string.

      If 'html', return the description with an html format.

  	Returns
  	-------
    description : str
        If format == 'str' : a carriage return separated enumaration of the members of the class experiment.

        If format == 'html' : an html version of the description

  	Examples
  	--------

    >>> import explanes as el
    >>> print(el.Experiment())
    project:
      name:
      description:
      author: no name
      address: noname@noorg.org
      runId: ...
    factor:
    parameter:
    metric:
    path:
      input:
      processing:
      storage:
      output:
    host: []

    >>> import explanes as el
    >>> el.Experiment().__str__(format='html')
    '<div>project: </div><div>  name: </div><div>  description: </div><div>  author: no name</div><div>  address: noname@noorg.org</div><div>  runId: ...</div><div>factor: </div><div>parameter: </div><div>metric: </div><div>path: </div><div>  input: </div><div>  processing: </div><div>  storage: </div><div>  output: </div><div>host: []</div><div></div>'
    """
    description = ''
    for atr in self._atrs:
      if type(inspect.getattr_static(self, atr)) != types.FunctionType:
        if type(self.__getattribute__(atr)) == types.SimpleNamespace:
          description += atr+': \r\n'
          for sns in self.__getattribute__(atr).__dict__.keys():
            description+='  '+sns+': '+str(self.__getattribute__(atr).__getattribute__(sns))+'\r\n'
        elif isinstance(self.__getattribute__(atr), str) or isinstance(self.__getattribute__(atr), list):
          description+=atr+': '+str(self.__getattribute__(atr))+'\r\n'
        else:
          description+=atr+': \r\n'+str(self.__getattribute__(atr))#+'\r\n'
    if format == 'html':
      description = '<div>'+description.replace('\r\n', '</div><div>').replace('\t', '&emsp;')+'</div>'
    return description

  def sendMail(
    self,
    title='',
    body=''):
    """Send an email to the email address given in experiment.project.address.

    Send an email to the experiment.project.address email address using the smtp service from gmail. For privacy, please consider using a dedicated gmail account by setting experiment._gmailId and experiment._gmailAppPassword. For this, you will need to create a gmail account, set two-step validation and allow connection with app password (see https://support.google.com/accounts/answer/185833?hl=en).

    Parameters
    ----------

    title : str
      the title of the email in plain text format

    body : str
      the body of the email in html format

    Examples
    --------
    >>> import explanes as el
    >>> e=el.experiment.Experiment()
    >>> e.project.address = 'mathieu.lagrange@cnrs.fr'
    >>> e.sendMail('hello', '<div> good day </div>')
    Sent message entitled: [explanes]  id ... hello ...

    """
    header = 'From: expLanes mailer <'+self._gmailId+'@gmail.com> \r\nTo: '+self.project.author+' '+self.project.address+'\r\nMIME-Version: 1.0 \r\nContent-type: text/html \r\nSubject: [explanes] '+self.project.name+' id '+self.project.runId+' '+title+'\r\n'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(self._gmailId+'@gmail.com', self._gmailAppPassword)
    server.sendmail(self._gmailId, self.project.address, header+body+'<h3> '+self.__str__(format = 'html')+'</h3>')
    server.quit
    print('Sent message entitled: [explanes] '+self.project.name+' id '+self.project.runId+' '+title+' on '+time.ctime(time.time()))

  def do(
    self,
    mask,
    function=None,
    *parameters,
    nbJobs=1,
    progress=True,
    logFileName='',
    mailInterval=0
    ):
    """Operate the function with parameters on the :term:`settings<setting>` set generated using :term:`mask`.

    Operate a given function on the setting set generated using mask. The setting set can be browsed in parallel by setting nbJobs>1. If logFileName is not empty, a faulty setting do not stop the execution, the error is stored and another setting is executed. If progress is set to True, a graphical display of the progress through the setting set is displayed.

    This function is essentially a wrapper to the function :meth:`explanes.factor.Factor.do`.

    Parameters
    ----------

    mask : a list of literals or a list of lists of literals
      :term:`mask` used to specify the :term:`settings<setting>` set

    function : function(:class:`~explanes.factor.Factor`, :class:`~explanes.experiment.Experiment`, \*parameters) (optional)
      A function that operates on a given setting within the experiment environnment with optional parameters.

      If None, a description of the given setting is shown.

    *parameters : any type (optional)
      parameters to be given to the function.

    nbJobs : int > 0 (optional)
      number of jobs.

      If nbJobs = 1, the setting set is browsed sequentially in a depth first traversal of the settings tree (default).

      If nbJobs > 1, the settings set is browsed randomly, and settings are distributed over the different processes.

    progress : bool (optional)
      display progress of scheduling the setting set.

      If True, use tqdm to display progress (default).

      If False, do not display progress.

    logFileName : str (optional)
      path to a file where potential errors will be logged.

      If empty, the execution is stopped on the first faulty setting (default).

      If not empty, the execution is not stopped on a faulty setting, and the error is logged in the logFileName file.

    mailInterval : float (optional)
      interval for sending email about the status of the run.

      If 0, no email is sent (default).

      It >0, an email is sent as soon as an setting is done and the difference between the current time and the time the last mail was sent is larger than mailInterval.

    See Also
    --------

    explanes.factor.Factor.do

    Examples
    --------

    >>> import time
    >>> import random
    >>> import explanes as el

    >>> e=el.experiment.Experiment()
    >>> e.factor.factor1=[1, 3]
    >>> e.factor.factor2=[2, 5]

    >>> # this function displays the sum of the two modalities of the current setting
    >>> def myFunction(setting, experiment):
    ...  time.sleep(random.uniform(0, 2))
    ...  print('{}+{}={}'.format(setting.factor1, setting.factor2, setting.factor1+setting.factor2))

    >>> # sequential execution of settings
    >>> nbFailed = e.do([], myFunction, nbJobs=1, progress=False)
    1+2=3
    1+5=6
    3+2=5
    3+5=8
    >>> # arbitrary order execution of settings due to the parallelization
    >>> nbFailed = e.do([], myFunction, nbJobs=3, progress=False) # doctest: +SKIP
    3+2=5
    1+5=6
    1+2=3
    3+5=8
    """

    return self.factor.mask(mask).do(function, self, *parameters, nbJobs=nbJobs, progress=progress, logFileName=logFileName, mailInterval=mailInterval)

  def cleanDataSink(
    self,
    path,
    mask=[],
    reverse=False,
    force=False,
    selector='*',
    settingEncoding={},
    archivePath = None
    ):
    """ Perform a cleaning of a data sink (directory or h5 file).

    This method is essentially a wrapper to :meth:`explanes.factor.Factor.cleanDataSink`.

    Parameters
    ----------

    path : str
      If has a / or \\\, a valid path to a directory or .h5 file.

      If has no / or \\\, a member of the NameSpace experiment.path.

    mask : a list of literals or a list of lists of literals (optional)
      :term:`mask` used to specify the :term:`settings<setting>` set

    reverse : bool (optional)
      If False, remove any entry corresponding to the setting set (default).

      If True, remove all entries except the ones corresponding to the setting set.

    force: bool (optional)
      If False, prompt the user before modifying the data sink (default).

      If True, do not prompt the user before modifying the data sink.

    selector : str (optional)
      end of the wildcard used to select the entries to remove or to keep (default: '*').

    settingEncoding : dict (optional)
      format of the id describing the :term:`setting`. Please refer to :meth:`explanes.factor.Factor.id` for further information.

    archivePath : str (optional)
      If not None, specify an existing directory where the specified data will be moved.

      If None, the path explanes.experiment.Experiment._archivePath is used (default).

    See Also
    --------

    explanes.factor.Factor.cleanDataSink, explanes.factor.Factor.id

    Examples
    --------

    >>> import explanes as el
    >>> import numpy as np
    >>> import os
    >>> e=el.experiment.Experiment()
    >>> e.path.output = '/tmp/test'
    >>> e.setPath()
    >>> e.factor.factor1=[1, 3]
    >>> e.factor.factor2=[2, 4]
    >>> def myFunction(setting, experiment):
    ...   np.save(experiment.path.output+'/'+setting.id()+'_sum.npy', setting.factor1+setting.factor2)
    ...   np.save(experiment.path.output+'/'+setting.id()+'_mult.npy', setting.factor1*setting.factor2)
    >>> nbFailed = e.do([], myFunction, progress=False)
    >>> os.listdir(e.path.output)
    ['factor1_3_factor2_2_sum.npy', 'factor1_3_factor2_2_mult.npy', 'factor1_3_factor2_4_mult.npy', 'factor1_1_factor2_2_sum.npy', 'factor1_1_factor2_4_mult.npy', 'factor1_3_factor2_4_sum.npy', 'factor1_1_factor2_2_mult.npy', 'factor1_1_factor2_4_sum.npy']

    >>> e.cleanDataSink('output', [0], force=True)
    >>> os.listdir(e.path.output)
    ['factor1_3_factor2_2_sum.npy', 'factor1_3_factor2_2_mult.npy', 'factor1_3_factor2_4_mult.npy', 'factor1_3_factor2_4_sum.npy']

    >>> e.cleanDataSink('output', [1, 1], force=True, reverse=True, selector='*mult*')
    >>> os.listdir(e.path.output)
    ['factor1_3_factor2_2_sum.npy', 'factor1_3_factor2_4_mult.npy', 'factor1_3_factor2_4_sum.npy']

    Here, we remove all the files that match the wildcard *mult* in the directory /tmp/test that do not correspond to the settings that have the first factor set to the second modality and the second factor set to the second modality.

    >>> import explanes as el
    >>> import tables as tb
    >>> e=el.experiment.Experiment()
    >>> e.path.output = '/tmp/test.h5'
    >>> e.factor.factor1=[1, 3]
    >>> e.factor.factor2=[2, 4]
    >>> e.metric.sum = ['']
    >>> e.metric.mult = ['']
    >>> def myFunction(setting, experiment):
    ...   h5 = tb.open_file(experiment.path.output, mode='a')
    ...   sg = experiment.metric.addSettingGroup(h5, setting, metricDimension={'sum': 1, 'mult': 1})
    ...   sg.sum[0] = setting.factor1+setting.factor2
    ...   sg.mult[0] = setting.factor1*setting.factor2
    ...   h5.close()
    >>> nbFailed = e.do([], myFunction, progress=False)
    >>> h5 = tb.open_file(e.path.output, mode='r')
    >>> print(h5)
    /tmp/test.h5 (File) ''
    Last modif.: '...'
    Object Tree:
    / (RootGroup) ''
    /factor1_1_factor2_2 (Group) 'factor1 1 factor2 2'
    /factor1_1_factor2_2/mult (Array(1,)) 'mult'
    /factor1_1_factor2_2/sum (Array(1,)) 'sum'
    /factor1_1_factor2_4 (Group) 'factor1 1 factor2 4'
    /factor1_1_factor2_4/mult (Array(1,)) 'mult'
    /factor1_1_factor2_4/sum (Array(1,)) 'sum'
    /factor1_3_factor2_2 (Group) 'factor1 3 factor2 2'
    /factor1_3_factor2_2/mult (Array(1,)) 'mult'
    /factor1_3_factor2_2/sum (Array(1,)) 'sum'
    /factor1_3_factor2_4 (Group) 'factor1 3 factor2 4'
    /factor1_3_factor2_4/mult (Array(1,)) 'mult'
    /factor1_3_factor2_4/sum (Array(1,)) 'sum'
    >>> h5.close()

    >>> e.cleanDataSink('output', [0], force=True)
    >>> h5 = tb.open_file(e.path.output, mode='r')
    >>> print(h5)
    /tmp/test.h5 (File) ''
    Last modif.: '...'
    Object Tree:
    / (RootGroup) ''
    /factor1_3_factor2_2 (Group) 'factor1 3 factor2 2'
    /factor1_3_factor2_2/mult (Array(1,)) 'mult'
    /factor1_3_factor2_2/sum (Array(1,)) 'sum'
    /factor1_3_factor2_4 (Group) 'factor1 3 factor2 4'
    /factor1_3_factor2_4/mult (Array(1,)) 'mult'
    /factor1_3_factor2_4/sum (Array(1,)) 'sum'
    >>> h5.close()

    >>> e.cleanDataSink('output', [1, 1], force=True, reverse=True, selector='*mult*')
    >>> h5 = tb.open_file(e.path.output, mode='r')
    >>> print(h5)
    /tmp/test.h5 (File) ''
    Last modif.: '...'
    Object Tree:
    / (RootGroup) ''
    /factor1_3_factor2_4 (Group) 'factor1 3 factor2 4'
    /factor1_3_factor2_4/mult (Array(1,)) 'mult'
    /factor1_3_factor2_4/sum (Array(1,)) 'sum'
    >>> h5.close()

    Here, the same operations are conducted on a h5 file.
    """
    if not archivePath:
      archivePath=self._archivePath
    if '/' not in path and '\\' not in path:
      path = self.__getattribute__('path').__getattribute__(path)
    if path:
      self.factor.mask(mask).cleanDataSink(path, reverse, force, selector, settingEncoding, archivePath)

  def clean(
    self,
    mask=[],
    reverse=False,
    force=False,
    selector='*',
    settingEncoding={},
    archivePath = None
    ):
    """Clean all relevant directories specified in the NameSpace explanes.Experiment.experiment.path.

    Apply :meth:`explanes.experiment.Experiment.cleanDataSink` on each relevant directories specified in the NameSpace explanes.experiment.Experiment.path.

    See Also
    --------

    explanes.experiment.Experiment.cleanDataSink

    Examples
    --------

    >>> import explanes as el
    >>> e=el.experiment.Experiment()
    >>> e.path.output = '/tmp/test'
    >>> e.setPath()
    >>> e.clean()
    checking input path
    checking processing path
    checking storage path
    checking output path

    """
    for sns in self.__getattribute__('path').__dict__.keys():
      print('checking '+sns+' path')
      self.cleanDataSink(sns, mask, reverse, force, selector, settingEncoding,
      archivePath)

class Path:
    def __setattr__(
      self,
      name,
      value
      ):
      return object.__setattr__(self, name, os.path.expanduser(value))


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    #doctest.run_docstring_examples(run, globals(), optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)
