/** Test if the method submitted by the student exceeded a certain time limit
Author: Sally Hamouda */

import java.util.*;
import java.lang.*;
import java.io.*;
import java.lang.reflect.Method;

class failOnTimeout
{
        public static  long fTimeout;
	public static boolean fFinished= false;
	public static Throwable fThrown= null;
   
	public static String methodName;
        public static String className;
    
        public static Class[] parametersTypes;
        public static Object[] parametersValues;
        public static Object returnedValue;
       // pass the class name, method name , timeout period in seconds , passed parameter types , passed parameters values 
	public failOnTimeout(String cName, String mName, long timeout , Class[] pTypes, Object [] pValues )
	{
		className = cName;
		methodName = mName;
		fTimeout = timeout;
		parametersTypes = pTypes;
                parametersValues = pValues;
		
	}
	public static void evaluate() throws Throwable {
	        Thread thread= new Thread() {
		@Override
		public void run() {
		 try {
		  Object theClass = Class.forName(className).newInstance();
		  Method theMethod = theClass.getClass().getDeclaredMethod(methodName, parametersTypes);					
                  returnedValue = theMethod.invoke(theClass , parametersValues);	
		  fFinished= true;
		 } 
                 catch (Throwable e) {
		  fThrown= e;
		 }
	       }
	 };
	
        	thread.start();
		thread.join(fTimeout);
		if (fFinished)
			return;
		if (fThrown != null)
			throw fThrown;
		Exception exception= new Exception(String.format(
				"test timed out after %d milliseconds", fTimeout));
		exception.setStackTrace(thread.getStackTrace());
		throw exception;
	}
}

