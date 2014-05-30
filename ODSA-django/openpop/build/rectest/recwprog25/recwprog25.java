/** Test program for recursion programming exercise.
Author: Sally Hamouda */
//Exercise 25: this function takes a set of integers and a target number, your goal is to find whether a subset of those numbers that sums to the target number. For example, given the set 3,7,1,8,-3 and the target sum 4, the subset 3,1 sums to 4. On the other hand, if the target is 2 then the result is false. It is only required to return true or false.


import java.io.*;
import java.util.Random;

public class studentrecwprog25
{

 public static  boolean modelisSubsetSum(int set[], int n, int sum)
{	
if (sum == 0)
   return true;
		
if (n == 0 && sum != 0)
   return false;
		
if (set[n-1] > sum)
    return modelisSubsetSum(set, n-1, sum);
		
return modelisSubsetSum(set, n-1, sum)|| modelisSubsetSum(set, n-1, sum-set[n-1]);		
}

 public static void main(String [ ] args) 
{
  
    boolean SUCCESS = false;
   
    Random randNumGenerator = new Random();
    
    int[] numbers = new int[10];
    for (int i=0; i< numbers.length; i++)
    {
       numbers[i] = (randNumGenerator.nextInt(100)+1);
    }
   
    int sum = numbers[randNumGenerator.nextInt(9)];

    if (isSubsetSum(numbers, numbers.length, sum)== modelisSubsetSum(numbers, numbers.length , sum)) SUCCESS = true;

    try{

     PrintWriter output = new PrintWriter("output");

     if (SUCCESS) { 
   
      output.println("Well Done!");
      output.close();
     }
    else 
    {
     output.println("Try Again! Incorrect answer!");
     output.close();
    }
  
    }
      catch (IOException e) {
	e.printStackTrace();
    }

  }

  
