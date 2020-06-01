"""
ds_utils.py

A library of miscellaneous utils that I find I use often. 

Version 1.0

dsinfield6@gmail.com/ Telegram or signal:omotforest 

Released under GPL

Use at your own risk. Subject to update or change at any time.

"""
import os
#import sys
import getpass
import platform
version="1.0"
ARG_NOT_FOUND=False
class config():
    """
    Config File Helper Class
    
    Config files are in the format:
        #start comments
        ParameterName1 value1
        ParameterName2 value2
        .
        .
        .
        #endcomments
    Assumes values are one word when reading. Anything after a second space is ignored.
        
    Constructor takes 1 arguments
        filename - the name of the file only the path will be derived depejding on the operating system
                     Linux - will be a hidden file the user's home directory
                     Windows will be a file in the same directory as the application
                     Other will cause an exception
     """
    _config_comments=""
    _config_end_comments=""
    platform_supported=False
    config_file_name=""
    config_file_path=""
    def __init__(self, filename):
        #TODO: move comments and endcomments to write ecause they are not needed when we are reading
        #For Linux the config file will be \home\$USER\$filename
        #for windows it will be in the same directory as the executable
        self.config_filename=filename
        if platform.platform().find("Linux")>-1:
            self.platform_supported=True
            #set file location
            print("setting Linux file location")
            self.config_file_path='/home/'+getpass.getuser()+'/.'+self.config_filename
        elif platform.platform().find("Windows")>-1:
            self.platform_supported=True
            #set file location
            self.config_file_path=os.path.dirname(os.path.abspath(__file__))+'/'+self.config_filename
        else:
            #platform is not supported
            raise Exception("Platform {0} not supported".format(platform.platform()))
            pass
        #print ("filepath="+self.config_file_path)
    def readParameter(self, parametername):
        """
        Read the parameter from the file
            Returns False if not found
        """
        parameter=False
        if self.platform_supported:
            if os.path.exists(self.config_file_path):
                file=open(self.config_file_path, 'r')
                while(True):
                    line=file.readline()
                    if not line:
                        break;
                    if(len(line)>2):
                        if not line.strip()[0]=='#':
                            if line.strip().startswith(parametername):
                                try:
                                    parameter=line.split(' ')[1].strip()
                                except:
                                    parameter=False
                file.close()
            #print("in readparameter path="+self.config_file_path)
        return (parameter)
    def writeFile(self, dictParams, comments="", endcomments=""):
        """
            dictParams - a dictionary of parameters e.g {name1 : value1, name2 : value2}
            comments - a file header. Optional, default is empty string
            endcomments - a footnote. Optional, default is an empty string.
                       For neatness when doing a cat /n will be appended
        """

        if self.platform_supported:
            if os.path.exists(self.config_file_path):
                os.remove(self.config_file_path)
            file=open(self.config_file_path, 'w')
            file.writelines(comments)
            for p in dictParams:
                file.writelines(p+' '+dictParams[p]+"\n")
            file.writelines(endcomments+"\n")
            file.close()
    def getConfigPath(self):
        """
        Accessor function for file path property
        Call with object reference as parameter
        """
        return self.config_file_path
##### end config class
def makeDirectory(dirPath):
    """
    Usage makeDirectory(directory_path)

    Makes the directory in dirPath if it does not exist

    Throws exception if it fails.
    """
    try:
        if (not os.path.exists(dirPath)):
            os.mkdir(dirPath)
    except:
        raise Exception("In makeDirecory. Could not create {0}".format(dirPath))

def InputUntil(prompt, acceptable, case_sensitive=True, tries=0):
    """
    Usage InputUntil(prompt,acceptable_input,[case sensitive=True],[tries=0])
    Parameters:
        prompt - Prompt to be displayed (the acceptable terms will be listed)
        acceptable_input - String containing acceptable responses
        [case_sensitive] if false ignores case.; Default is True
        [tries] - Attempts before raisin an error.
    Keeps gettin input until one of the terms in acceptable is found. Works best for single characters
    See InputUntilList(prompt, acceptable, tries) for a word version
    
    You should still check the returned input because in YNC, YN will match.
    """
    a="*"
    count=0
    if not case_sensitive:
        acceptable=acceptable.upper()
    while (True):
        a=input(prompt+"("+acceptable+"):")
        ca=a
        if not case_sensitive:
            ca=a.upper()
        if acceptable.find(ca) >-1:
            break
        if tries>0:
            count+=1
        if count > tries:
            raise Exception("Too many tries")
            
    return a
def InputUntilList(prompt, acceptable, case_sensitive=True,  tries=0):
    """
    Input until one of the items on the list is typed or the number of tries is reached.
    Returns the actual answer typed (irrespective of the case sensitive flag.
    Raises an error if tries exceeded catch it in your code to handle it.

    For single letter (eg YN), the InputUntil in this module might be what you are looking for
  
    Usage InputUntil(prompt,acceptable_input, [case_sensitive=True], [tries=0])
    Parameters:
        prompt - Prompt to be displayed (the acceptable terms will be listed)
        acceptable_input - list containing acceptable responses

        case_sensitve - David DAVID, daVid all match david if this is false
        tries - Number of attempts until an error is raised. Set to <1 for infnite
    """
    trycount=1
    a="***not found***"
    ps=""
    test=[]
    temp=[]
    for i in acceptable:
        test.append(str(i))
        ps="\n"+ps
    if case_sensitive==False:
        for p in test:
            temp.append(p.upper())
        test=temp
    while(True):
        a=input(prompt)
        ca=a
        if case_sensitive==False:
            ca=a.upper()
        if ca in test:
            break
        if(tries>0):
            trycount+=1

        if trycount > tries:
                raise Exception("Too many tries")

    return a
def getParameterValue(parametername, args,  unitary=False):
    """
    Gets the command line parameter wih the name in parametername.
    Assumes the parameters are in -name value pairs.
    Longname parameters in the form --long_name value are supported but you must supply the --
    Parameters with no value are not supported. (Coming soon: Optional argument to specify standalone which returns True/False)
    Usage: getParameterValue(parametername,args)
    Parameters:
        parametername - the name of the parameter if no - then one is prepended
        args - usually sys.argv. If you want to use another string you need a placeholder where the program name would be
               e.g ["params",  "-p", "param1","-p2"] param2 works as expected
        unitary - will not look for, a value just the presence or absence of a parameter
    """
    retval=ARG_NOT_FOUND
    if (parametername[0]!="-"):
        parametername="-"+parametername
    count=0
    if unitary:
        while(count<len(args)-1):
            if args[count]==parametername:
                retval=True
            count+=1
    else:
        while (count < len(args)-1):
            if args[count]==parametername:
                retval=args[count+1]
                break
            count+=1
    return retval
#################
class Searches():
    """
    A class to contain search functions.
    
    Initialisation
    __init__(head, tail,source,start=0,ignorcase=false,inclusivefind=false)
        head - string to search from
        tail - string to search to
        start - integer position to start search. Optional. Default=0
        ignorecase - set to true to make case insensitive. Optional. Default=false
        inclusivefind - return the string from the start of head the end of tail. Optional.
        overlapsearch - if True sets newstart to start+1 
            default is to return the string from the end of head to the beginning of tail
     NB init calls get head to tail once so results of the first search are available after initialisation
    Reading results
        newstart - set to the end of the head
        result - set tp the string found or "" empty if not found
        resultstatus - text description of result of search
        resultsuccess - set to True if head and tail were found.
        EOF - set to true if the search extends past end of file
        listAll[] - set only if getAll has been called
    
    """
    #initialised params
    head=""
    tail=""
    start=0    
    source=""
    inclusivefind=False
    ignorecase=False
    overlapsearch=False
   #return parameters
    newstart=0
    result=""
    resultstatus=""
    resultsuccess=False
    EOF=False
    listAll=[]
    #intenal parameters
    _searchin=""
    def __init__(self, head, tail, source, start=0, ignorecase=False,  inclusivefind=False,  overlapsearch=False):
        self.head=head
        self.tail=tail
        self.start=start
        self.source=source
        self.ignorecase=ignorecase
        self.inclusivefind=inclusivefind
        self.overlapsearch=overlapsearch
        if ignorecase:
            self._searchin=source.upper()
        else: 
            self._searchin=source
        self.listAll=[]
        self.getHeadtoTail(head, tail, start)
#        return
    def getHeadtoTail(self, head, tail, start=False):
        if self.ignorecase:
            head=head.upper()
            tail=tail.upper()
        #print("head is:{0} tail is {1}".format(head, tail))
        if not start:
            s=self.newstart
        else: 
            s=start
        print ("Searching for head from {0} Length of listAll is:{1} ".format(str(s), str(len(self.listAll))))
        s=self._searchin.find(head, s)
        #print("Searching for tail from "+str(s))
        if (s>-1):
            e=self._searchin.find(tail, s+len(head))
            #print("In getHeadtoTail e is {0}".format(e))
            if e < 1:
                self.resultstatus="Could not find the tail {0}. We have reached the end.".format(tail)
                self.resultsuccess=False
                self.result=''
                self.EOF=True
            elif e<s:              
                self.resultstatus="Search has started to go backwards. Assuming end of file"
                self.resultsuccess=False
                self.result=""
                self.EOF=True
            else:
                #rint ("!!!in getheadto tail we are in success!!! s={0} e={1}".format(s, e))
                self.resultstatus = "Success"
                if self.inclusivefind:
                    self.result=head+self.source[int(s)+len(head):(e)]+tail
                else:
                    self.result=self.source[int(s)+len(head):(e)]
                self.resultsuccess=True
                #print("updating new start to {0}".format(str(e)))
                if not self.overlapsearch:
                    self.newstart=e
                else:
                    self.newstart=s+1
                #print("newstart is {0}".format(str(self.newstart)))
                self.EOF=False
        else:
                self.resultstatus="Could not find the head {0}".format(head)
                self.result=""
                self.resultsuccess=False
                self.EOF=True
        #print ("url="+url)
        
        return (self)
        
    def getAll(self, head, tail):
        #get the first one into a list
        if self.resultsuccess:
            self.listAll.append(self.result)
        while(1):
            self.getHeadtoTail(head, tail, start=self.newstart)
            if self.resultsuccess:
              self.listAll.append(self.result) 
            if self.EOF:
                break
        return self
        
       
class ANSI:
    """    
    GetANSI(text,foreback,colour,style)
    text - text to print
    forecolour - [black|red|green|yellow|blue|magenta|cyan|white]
    backcolour - [black|red|green|yellow|blue|magenta|cyan|white]
    style - [normal|bold|italic|underline|inverse|strikethough]
    
    Returns a string with ansi precursors to set foreground and background
    colours and style. Set to normal after printing.
    
    Most terminals support 8 colours. Some will not understand bold.
    
    Out of range parameters throw a dictionary error
    
    Colours supported:
        black
        red
        green
        yellow
        blue
        magenta
        cyan
        white
    Styles supported:
        normal
        bold
        italic
        underline
        inverse
        strikethrough
    
    Example: set foreground to red
    	print GetANSI('this is red text','red','none','none')
    Example: set foreground bold red, background cyan
    	print GetANSI('set properties','red','cyan','bold')
"""
    dictForeBack={
    'fore' : 3,
    'back' : 4
    }
    dictColour={
    'black' : 0,
    'red' : 1,
    'green' : 2, 
    'yellow' : 3,
    'blue' : 4,
    'magenta' : 5,
    'cyan' : 6,
    'white' : 7
    }
    dictStyle={
    'normal' : 0,
    'bold': 1,
    'italic' : 3,
    'underline' :4,
    'inverse': 7,
    'strikethrough' : 9
    }
    pre="\033["
    post="m"
    tonormal=pre+'0m'


    def GetANSI(self, text,forecolour='',backcolour='',style=''):
        """
        Constructs an ansi string to create multicoloured terminal display
        Parameters
            text - the string to be output
            forecolour - the colour to set the foreground. Optional. Default=normal
            backcolour - the colour to set the background. Optional. Default=normal
            style - one of the styles in dictStyle
        Returns 
            A string decorated with ansi codes
            
        """
        #TODO: style combinations separated with + if possible
        retval=""
        if forecolour != '':
            retval=retval+self.pre+str(self.dictForeBack['fore'])+str(self.dictColour[forecolour])+self.post
        if backcolour != '':
            retval=retval+self.pre+str(self.dictForeBack['back'])+str(self.dictColour[backcolour])+self.post
        if style != '':
            retval=retval+self.pre+str(self.dictStyle[style])+self.post
        return (retval+text+self.tonormal)
    def __init__(self):
        pass


if(__name__=="__main__"):
    #put any cdode that should run on startup here
    pass

    

