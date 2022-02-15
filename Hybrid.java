import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.InputStreamReader;
import java.util.*;
import java.util.Map.Entry;

public class Hybrid{
    // ==========================================
    // === configurations

    // === data set info
    public static int n; // user number
    public static int m; // item number
    public static int num_train = 0; // number of the total (user, item) pairs in training data
    public static int numItemTaken = 20;

    // === input data file
    public static String fnTestData = "";
    public static String fnTrainData = "";
    public static String fnABPRResult = "";
    public static String fnFossilResult = "";

    // === evaluation
    public static int topK; 

    // === tradeoff
    public static float tradeoff;
    
    // =============================================================
    // === training data
    public static HashMap<Integer, HashSet<Integer>> TrainData = new HashMap<Integer, HashSet<Integer>>(); // user-item pairs
    public static HashMap<Integer, HashSet<Integer>> TrainData_item2user = new HashMap<Integer, HashSet<Integer>>(); // item-user pairs

    // === training data used for uniformly random sampling
    public static int[] indexUserTrain; // start from index "0", used to uniformly sample (u, i) pair
    public static int[] indexItemTrain; // start from index "0", used to uniformly sample (u, i) pair

    // === test data
    public static HashMap<Integer, HashSet<Integer>> TestData = new HashMap<Integer, HashSet<Integer>>();

    // === the whole set of items
    public static HashSet<Integer> itemSetWhole = new HashSet<Integer>();

    // === some statistics, start from index "1"
    public static int[] userRatingNumTrain; // to add up the related records of each user
    public static int[] itemRatingNumTrain; // to add up the related records of each item

    // === result list
    public static HashMap<Integer, ArrayList<Integer>> Fossil_list = new HashMap<>();
    public static HashMap<Integer, ArrayList<Integer>> ABPR_list = new HashMap<>();


    public static void main(String[] args) throws Exception{

        // ===
        readConfigurations(args);

        // =========================================================
        // === some statistics
        itemRatingNumTrain = new int[m+1];
        userRatingNumTrain = new int[n+1];
        // ===
        readData();

        // ===
        testRanking(TestData);
    }



    // =========================================
    // === function: read configurations
    private static void readConfigurations(String[] args){
        for(int k=0; k < args.length; ++k){
            if (args[k].equals("-n")) n = Integer.parseInt(args[++k]);
            else if (args[k].equals("-m")) m = Integer.parseInt(args[++k]);
            else if (args[k].equals("-topK")) topK = Integer.parseInt(args[++k]);
            else if (args[k].equals("-numItemTaken")) numItemTaken = Integer.parseInt(args[++k]);
            else if (args[k].equals("-fnTestData")) fnTestData = args[++k];
            else if (args[k].equals("-fnTrainData")) fnTrainData = args[++k];
            else if (args[k].equals("-fnABPRResult")) fnABPRResult = args[++k];
            else if (args[k].equals("-fnFossilResult")) fnFossilResult = args[++k];
            else if (args[k].equals("-tradeoff")) tradeoff = Float.parseFloat(args[++k]);

        }

        // === Print the configurations
        System.out.println(Arrays.toString(args));

        System.out.println("fnTrainData: " + fnTrainData);
        System.out.println("fnTestData: " + fnTestData);
        System.out.println("fnABPRResult: " + fnABPRResult);
        System.out.println("fnFossilResult: " + fnFossilResult);
        System.out.println("n: " + Integer.toString(n));
        System.out.println("m: " + Integer.toString(m));


        System.out.println("topK: " + Integer.toString(topK));
        System.out.println("numItemTaken: " + Integer.toString(numItemTaken));

        if(numItemTaken < 0){
            numItemTaken = Integer.MAX_VALUE;
        }
    }


    // =========================================
    // === function: read datasets
    public static void readData() throws Exception
    {
        // =========================================================
        BufferedReader br = new BufferedReader(new FileReader(fnTrainData));
        String line = null;
        while ((line = br.readLine())!=null)
        {
            String[] terms = line.split("\\s+|,|;");
            int userID = Integer.parseInt(terms[0]);
            int itemID = Integer.parseInt(terms[1]);

            // === add to the whole item set
            itemSetWhole.add(itemID);

            // ===
            userRatingNumTrain[userID] += 1; // to add up the related records of each user
            itemRatingNumTrain[itemID] += 1; // to add up the related records of each item

            // ===
            num_train += 1; // the number of total user-item pairs

            // === TrainData: user->items
            if(TrainData.containsKey(userID))
            {
                HashSet<Integer> itemSet = TrainData.get(userID);
                itemSet.add(itemID);
                TrainData.put(userID, itemSet);
            }
            else
            {
                HashSet<Integer> itemSet = new HashSet<Integer>();
                itemSet.add(itemID);
                TrainData.put(userID, itemSet);
            }

            // === TrainData: item->users
            if(TrainData_item2user.containsKey(itemID))
            {
                HashSet<Integer> userGroup = TrainData_item2user.get(itemID);
                userGroup.add(userID);
                TrainData_item2user.put(itemID, userGroup);
            }
            else
            {
                HashSet<Integer> userGroup = new HashSet<Integer>();
                userGroup.add(userID);
                TrainData_item2user.put(itemID, userGroup);
            }
        }
        br.close();
        // =========================================================

        // =========================================================
        br = new BufferedReader(new FileReader(fnTestData));
        line = null;
        while ((line = br.readLine())!=null)
        {
            String[] terms = line.split("\\s+|,|;");
            int userID = Integer.parseInt(terms[0]);
            int itemID = Integer.parseInt(terms[1]);

            // === add to the whole item set
            itemSetWhole.add(itemID);

            // === test data
            if(TestData.containsKey(userID))
            {
                HashSet<Integer> itemSet = TestData.get(userID);
                itemSet.add(itemID);
                TestData.put(userID, itemSet);
            }
            else
            {
                HashSet<Integer> itemSet = new HashSet<Integer>();
                itemSet.add(itemID);
                TestData.put(userID, itemSet);
            }
        }
        br.close();
        // =========================================================

        // =========================================================
        // === read Fossil result list
        // === data format: userid itemNum item_1 item_2 ... item_itemNum
        br = new BufferedReader(new InputStreamReader( new FileInputStream( fnFossilResult ) , "UTF-16"));
        line = null;
        boolean flag = false;
        while ((line = br.readLine())!=null)
        {
            if(line.startsWith("--- begin")){
                flag = true;
                continue;
            }
            if(line.startsWith("--- end"))
                flag = false;
            
            if(!flag)
                continue;

            String[] terms = line.split(" ");
            int userID = Integer.parseInt(terms[0]);
            int len = Math.min(Integer.parseInt(terms[1]), numItemTaken);

            ArrayList<Integer> tmp_ItemList = new ArrayList<>();
            for(int i=0; i<len; ++i){
                tmp_ItemList.add(Integer.parseInt(terms[2+i]));
            }
            Fossil_list.put(userID, tmp_ItemList);

            // =============== Debug ====================
            //System.out.println("user:" + userID + " list_size:" + tmp_ItemList.size());
        }
        br.close();
        // =========================================================

        // =========================================================
        // === read ABPR result list
        // === data format: userid itemNum item_1 item_2 ... item_itemNum
        br = new BufferedReader(new InputStreamReader( new FileInputStream( fnABPRResult ) , "UTF-16"));
        line = null;
        flag = false;
        while ((line = br.readLine())!=null)
        {
            if(line.startsWith("--- begin")){
                flag = true;
                
                
                continue;
            }
            if(line.startsWith("--- end"))
                flag = false;
            
            if(!flag){
                // ========= Debug ==============
                //System.out.println(line);
                continue;
            }

            String[] terms = line.split(" ");
            int userID = Integer.parseInt(terms[0]);
            int len = Math.min(Integer.parseInt(terms[1]), numItemTaken);

            ArrayList<Integer> tmp_ItemList = new ArrayList<>();
            for(int i=0; i<len; ++i){
                tmp_ItemList.add(Integer.parseInt(terms[2+i]));
            }
            ABPR_list.put(userID, tmp_ItemList);

            // =============== Debug ====================
            //System.out.println("user:" + userID + " list_size:" + tmp_ItemList.size() + " First-item:" + tmp_ItemList.get(0));
        }
        br.close();
        // =========================================================
    }


    public static void testRanking(HashMap<Integer, HashSet<Integer>> TestData)
    {
        // TestData: user->items
        // =========================================================
        float[] PrecisionSum = new float[topK+1];
        float[] RecallSum = new float[topK+1];
        float[] F1Sum = new float[topK+1];
        float[] NDCGSum = new float[topK+1];
        float[] OneCallSum = new float[topK+1];

        // === calculate the best DCG, which can be used later
        float[] DCGbest = new float[topK+1];
        for (int k=1; k<=topK; k++)
        {
            DCGbest[k] = DCGbest[k-1];
            DCGbest[k] += 1/Math.log(k+1);
        }

        // === number of test cases
        int UserNum_TestData = TestData.keySet().size();

        for(int u=1; u<=n; u++)
        {
            // === check whether the user $u$ is in the test set
            if (!TestData.containsKey(u))
            {
                continue;
            }

            // ===
            HashSet<Integer> itemSet_u_TrainData = new HashSet<Integer>();
            if (TrainData.containsKey(u))
            {
                itemSet_u_TrainData = TrainData.get(u);
            }
            HashSet<Integer> itemSet_u_TestData = TestData.get(u);

            // === the number of preferred items of user $u$ in the test data
            int ItemNum_u_TestData = itemSet_u_TestData.size();

            // === Prediction: Hybrid the result of ABPR and Fossil to generate new lists
            HashMap<Integer, Float> item2Prediction = new HashMap<>();
            item2Prediction.clear();
            Predict(u, item2Prediction, itemSet_u_TrainData);
            // =========================================================================            

            // === sort
            List<Entry<Integer,Float>> listY =
                    new ArrayList<Entry<Integer,Float>>(item2Prediction.entrySet());
            Collections.sort(listY, new Comparator<Entry<Integer,Float>>()
            {
                public int compare( Entry<Integer, Float> o1, Entry<Integer, Float> o2 )
                {
                    return o1.getValue().compareTo( o2.getValue() );
                }
            });

            // =========================================================
            // === Extract the topK recommended items
            int k=1;
            int[] TopKResult = new int [topK+1];
            Iterator<Entry<Integer, Float>> iter = listY.iterator();
            while (iter.hasNext())
            {
                if(k>topK)
                    break;

                Entry<Integer, Float> entry = (Entry<Integer, Float>) iter.next();
                int itemID = entry.getKey();
                TopKResult[k] = itemID;
                k++;
            }

            // ================== Debug ======================
            System.out.print("user:" + u + " ");
            for(int i=1; i<=topK; ++i){
                System.out.print(TopKResult[i] + " ");
            }
            System.out.println();
            // ================== Debug ======================


            // === TopK evaluation
            int HitSum = 0;
            float[] DCG = new float[topK+1];
            float[] DCGbest2 = new float[topK+1];
            for(k=1; k<=topK; k++)
            {
                // ===
                DCG[k] = DCG[k-1];
                int itemID = TopKResult[k];
                if ( itemSet_u_TestData.contains(itemID) )
                {
                    HitSum += 1;
                    DCG[k] += 1 / Math.log(k+1);
                }
                // === precision, recall, F1, 1-call
                float prec = (float) HitSum / k;
                float rec = (float) HitSum / ItemNum_u_TestData;
                float F1 = 0;
                if (prec+rec>0)
                {
                    F1 = 2 * prec*rec / (prec+rec);
                }
                PrecisionSum[k] += prec;
                RecallSum[k] += rec;
                F1Sum[k] += F1;
                // === in case the the number relevant items is smaller than k
                if (itemSet_u_TestData.size()>=k)
                {
                    DCGbest2[k] = DCGbest[k];
                }
                else
                {
                    DCGbest2[k] = DCGbest2[k-1];
                }
                NDCGSum[k] += DCG[k]/DCGbest2[k];
                // ===
                OneCallSum[k] += HitSum>0 ? 1:0;
            }

        }

        // =========================================================
        // === the number of users in the test data
        System.out.println( "The number of users in the test data: " + Integer.toString(UserNum_TestData) );

        // === precision@k
        for(int k=1; k<=topK; k++)
        {
            float prec = PrecisionSum[k]/UserNum_TestData;
            System.out.println("Prec@"+Integer.toString(k)+":"+Float.toString(prec));
        }
        // === recall@k
        for(int k=1; k<=topK; k++)
        {
            float rec = RecallSum[k]/UserNum_TestData;
            System.out.println("Rec@"+Integer.toString(k)+":"+Float.toString(rec));
        }
        // === F1@k
        for(int k=1; k<=topK; k++)
        {
            float F1 = F1Sum[k]/UserNum_TestData;
            System.out.println("F1@"+Integer.toString(k)+":"+Float.toString(F1));
        }
        // === NDCG@k
        for(int k=1; k<=topK; k++)
        {
            float NDCG = NDCGSum[k]/UserNum_TestData;
            System.out.println("NDCG@"+Integer.toString(k)+":"+Float.toString(NDCG));
        }
        // === 1-call@k
        for(int k=1; k<=topK; k++)
        {
            float OneCall = OneCallSum[k]/UserNum_TestData;
            System.out.println("1-call@"+Integer.toString(k)+":"+Float.toString(OneCall));
        }
        
    }


    private static void Predict(int u, HashMap<Integer, Float> item2Prediction, HashSet<Integer> itemSet_u_TrainData){
        for(int i=1; i<m; ++i){
            if( !itemSetWhole.contains(i) || itemSet_u_TrainData.contains(i))
                continue;
            
            // === predictions
            int id_fossil = Fossil_list.get(u).indexOf(i);
            int id_abpr = ABPR_list.get(u).indexOf(i);
            float pred = tradeoff * (id_fossil == -1 ? (m/2.0f) : (id_fossil + 1.0f) ) + (1.0f - tradeoff) * (id_abpr == -1 ? (m/2.0f) : (id_abpr + 1.0f) );
            item2Prediction.put(i, pred);
        }
    }
}