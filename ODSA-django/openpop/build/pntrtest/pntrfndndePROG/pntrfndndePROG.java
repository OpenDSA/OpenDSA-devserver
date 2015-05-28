/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 16:  prints the binary equivalent of an integer N
import java.io.*;
import java.util.Random;


public class studentpntrfndndePROG
{
 
 public static int modelfindNode( int x)
{
  return 4;
  
  
}
	
     
	
  public static void main(String [ ] args) {
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    int number=  randNumGenerator.nextInt(32);
    
	
	
    if (modelfindNode(number) == findNode(number)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Feedback");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
