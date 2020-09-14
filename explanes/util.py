import sys
import re

def constantColumn(
  table=None
):
  """Store which column(s) have the same value for all lines.


	Parameters
	----------

  table : list of equal size lists or None
    table of literals

	Returns
	-------

  indexes : list of booleans
    indexes of constant valued columns

  values : list of literals
    values of the constant valued columns

	See Also
	--------
  explanes.metric.reduce, explanes.metric.get

	Examples
	--------
  >>> import explanes as el
  >>> table = [['a', 'b', 1, 2], ['a', 'c', 2, 2], ['a', 'b', 2, 2]]
  >>> el.util.constantColumn(table)
  ([True, False, False, True], ['a', 'b', 1, 2])
  """

  indexes = [True] * len(table[0])
  values = [None] * len(table[0])

  for r in table:
      for cIndex, c in enumerate(r):
          if values[cIndex] == None:
              values[cIndex] = c
          elif values[cIndex] != c:
              indexes[cIndex] = False
  return (indexes, values)

def compressDescription(description, format='long', atomLength=2):
  """ reduce the number of letters for each word in a given description structured with underscores (pythonCase) or capital letters (camelCase).

	Parameters
	----------
  description : string
    The structured description

  format : string
    The expected format. 'long' (default) do not lead to any reduction. 'shortUnderscore' assumes pythonCase delimitation. 'shortCapital' assumes camelCase delimitation. 'short' attempts to perform reduction by guessing the type of delimitation.

	Returns
	-------

  compressedDescription : string
    The compressed description

	See Also
	--------

	Examples
	--------

  >>> import explanes as el
  >>> el.util.compressDescription('myVeryLongParameter', format='short')
  myvelopa
  >>> el.util.compressDescription('that_very_long_parameter', format='short', atomLength=3)
  thaverlonpar
  """

  if format == 'short':
    if '_' in description and not description.islower() and not description.isupper():
      print('The description '+description+' has underscores and capital. Explicitely states which delimeter shall be considered for reduction.')
      raise ValueError
    elif '_' in description:
      format = 'shortUnderscore'
    else:
      format = 'shortCapital'
  compressedDescription = description
  if 'shortUnderscore' in format:
    sf = ''.join([itf[0:atomLength] for itf in description.split('_')])
  if 'shortCapital' in format:
    sf = description[0:atomLength]+''.join([itf[0:atomLength] for itf in re.findall('[A-Z][^A-Z]*', description)]).lower()
  return sf

def query_yes_no(question, default="yes"):
  """Ask a yes/no question via input() and return their answer.

  The "answer" return value is True for "yes" or False for "no".

	Parameters
	----------

  question : string
    phrase presented to the user.
  default : string or None
    presumed answer if the user just hits <Enter>. It must be "yes" (the default), "no" or None (meaning an answer is required of the user).

	Returns
	-------

  answer : boolean
    True for "yes" or False for "no"
  """

  valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
  if default is None:
    prompt = " [y/n] "
  elif default == "yes":
    prompt = " [Y/n] "
  elif default == "no":
    prompt = " [y/N] "
  else:
    raise ValueError("invalid default answer: '%s'" % default)

  while True:
    sys.stdout.write(question + prompt)
    choice = input().lower()
    if default is not None and choice == '':
      return valid[default]
    elif choice in valid:
      return valid[choice]
    else:
      sys.stdout.write("Please respond with 'yes' or 'no' "
                           "(or 'y' or 'n').\n")


def runFromNoteBook():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

def runFromColab():
    try:
        import google.colab
        return True
    except:
        return False