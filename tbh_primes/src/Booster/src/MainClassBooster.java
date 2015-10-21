
import java.util.*;
import java.io.*;

import edu.stanford.nlp.parser.lexparser.LexicalizedParser;

public class MainClassBooster {
	
	public static final int TOTAL_SENTENCES=100; 
		
	public static void main(String[] args) throws FileNotFoundException {
		
		Scanner filein=new Scanner(new File("sentences.txt"));
		Vector<String> file=new Vector<String>();
		for(int z=0; z<TOTAL_SENTENCES && filein.hasNext(); z++) file.addElement(filein.nextLine());
		file=shuffle(file);
		
		int n=file.size(); // not z in case filein.hasNext() was false.
		
		int m=100;//m?
		
		double w[]=new double[n];
		for(int a=0; a<n; a++) {
			w[a]=1/(double)n;
		}
		
		LexicalizedParser lp=new LexicalizedParser("grammar/englishPCFG.ser.gz");
		ParserFeatures parser=new ParserFeatures();
		
		int t[]=new int[n];
		int correct[]=new int[n];
		
		for(int a=0; a<n; a++) {
			String line=file.elementAt(a);
			StringTokenizer st=new StringTokenizer(line, ";");
			
			correct[a]=Integer.parseInt(st.nextToken());
			
			String sentence=st.nextToken();
			sentence=removeWords(sentence);
			
			if(sentence.length()>0 && isntJustSpaces(sentence)) {
				t[a]=parser.getFeatures(sentence, lp)[0]; // just one feature for now.
				
			}
			// t = { 1, 3, 7, 14, 18... }
		}
		
		int y[]=new int[m];			
		for(int b=0; b<m; b++) y[b]=0;
		
		double[] alphaArr=new double[m];
		
		
		// m: number of iterations of trying different thresholds
		for(int a=0; a<m; a++) {
			double total=0;
			
			int maxOccurrances=(int)findBiggest(t)[0]+2;
			double totalarr[]=new double[maxOccurrances*2];
			
			for(int b=0; b<maxOccurrances*2; b+=2) { // because oooo has |o|o|o|o| left-right-*shift*-left-right-*shift*...
				for(int c=0; c<n; c++) {// find all of the temptotals.
					if(t[c]<b/2 && correct[c]==0) totalarr[b]+=w[c];
					if(t[c]>=b/2 && correct[c]==1) totalarr[b]+=w[c];

					if(t[c]<b/2 && correct[c]==1) totalarr[b+1]+=w[c];
					if(t[c]>=b/2 && correct[c]==0) totalarr[b+1]+=w[c];
				}
			}
			double[] arr=findSmallest(totalarr);
			
			total=arr[0];
			y[a]=(int)arr[1];
			
			double total2=0;
			for(int b=0; b<n; b++) {
				total2+=w[n];
			}
			
			double e=total/total2;
			double alpha=Math.log((1-e)/e);
			
			for(int b=0; b<n; b++) {
				int tru=1;
				boolean left;
				if(y[a]%2==0) left=true;
				else left=false;
				int below=y[a]/2;
				
				if(t[b]<below && left && correct[b]==1) tru=0; //if the guess was right 
				if(t[b]>=below && left && correct[b]==0) tru=0; //if the guess was right 
				
				if(t[b]>=below && !left && correct[b]==1) tru=0;
				if(t[b]<below && !left && correct[b]==0) tru=0;
				
				w[n]=w[n]*Math.exp(alpha*tru);
			}
			alphaArr[a]=alpha;
		}
		// find final classifier
	}
	
	public static String removeWords(String beforeword) {
		String word=beforeword;
		String[] bad={"<noise>", "chair", "hal", "wheelchair", "<uh>", "<>", "<um>", "_"};
		for(String s : bad) {
			while(word.contains(s)) {
				if(!s.equals("_")) word=word.substring(0, word.indexOf(s))+word.substring(word.indexOf(s)+s.length(), word.length());
				else word=word.substring(0, word.indexOf(s))+" "+word.substring(word.indexOf(s)+s.length(), word.length());
			}
		}
		return(word);
	}
	
	public static boolean isntJustSpaces(String s) {
		for(int a=0; a<s.length(); a++) {
			if(s.charAt(a)!=' ') return(true);
		}
		return(false);
	}
	
	public static int countWords(String s) {
		int words=0;
		int lastspaceindex=-1;
		for(int a=0; a<s.length(); a++) {
			if((s.charAt(a)!=' ')&&(a-lastspaceindex>1)) {
				words++;
				lastspaceindex++;
			}
		}
		return(words);
	}
	
	public static Vector<String> shuffle(Vector<String> a) {
		Vector<String> shuffled=new Vector<String>();
		while(!a.isEmpty()) {
			int rand=(int)(Math.random()*a.size());
			shuffled.addElement(a.elementAt(rand));
			a.removeElementAt(rand);
		}
		return(shuffled);
	}
	/*
	 * Returns an array with the smallest element of that array,
	 * and the index of that element is stored in the second index.
	 */
	public static double[] findSmallest(double[] arr) {
		double smallest=arr[0];
		double index=0;
		for(int a=1; a<arr.length; a++) {
			if(arr[a]<smallest) {
				smallest=arr[a];
				index=a;
			}
		}
		double[] returnthis={smallest, index};
		return(returnthis);
	}
	public static int[] findBiggest(int[] arr) {
		int biggest=arr[0];
		int index=0;
		for(int a=1; a<arr.length; a++) {
			if(arr[a]>biggest) {
				biggest=arr[a];
				index=a;
			}
		}
		int[] returnthis={biggest, index};
		return(returnthis);
	}
	
}