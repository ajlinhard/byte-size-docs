# Pyspark Setup
The setup below was for Spark 3.5.1 or 3.4.3. 
install complete date => 2024-10-12
install machine os => windows 10

Requirements:
- Java (Version is important! Not the latest Java 8, 11 or 17)
  - https://www.oracle.com/java/technologies/downloads/#jdk17-windows
  - https://docs.oracle.com/en/java/javase/17/install/installation-jdk-microsoft-windows-platforms.html#GUID-A7E27B90-A28D-4237-9383-A58B416071CA
- Python
  - Python later versions have issues interacting with Java. I installed Python3.8 to get this to work. look at the PySpark YAML I made in this folder.
  - https://spark.apache.org/docs/latest/api/python/getting_started/install.html#using-conda
- WinUtils
  - https://github.com/kontext-tech/winutils
  - Version 3.3.0 was used for this version
  - Download ALL the files!! or at least the .dll
- Spark
  - https://spark.apache.org/downloads.html
 
### Commands
- Add Environment Variables
  - SPARK_HOME
  - HADOOP_HOME
  - JAVA_HOME
  - PATH
    - %SPARK_HOME%\bin
    - %HADOOP_HOME%\bin
    - %JAVA_HOME%\bin
- Calling spark-shell for scala and pyspark for python
- install findspark python package


## Learnings
- With the environment variables set on the machine you can call pyspark in any anaconda environment.
- Java versions matters for Spark since the Security Manager is being phased out after JDK17.
  - PySpark, which uses Py4J to communicate between Python and Java, is likely using code that relies on these deprecated security APIs.

## Outstanding Questions
- There are spark environment variables I can set. JAVA_HOME, SPARK_HOME
  - How do I set these in a YML or script

## Links/Videos Used
- https://www.youtube.com/watch?v=rYY0LFdmI8s
  - Read my notes above because he forgot to mention a couple things like Java Version and is hitting it with Scala.
- https://www.youtube.com/watch?v=AL6zTrlyAhc
  - Helpful but does not cover the environment variables
- https://sparkbyexamples.com/pyspark/how-to-install-and-run-pyspark-on-windows/#google_vignette
  - Helpful for written instructions and had helpful other options at the bottom

=================================================================================================================
## Java Version Important Note
Based on the search results, Spark does not officially support JDK 23 yet. Here's a summary of the current Spark and Java version compatibility:

1. The latest stable Spark version (3.5.1) officially supports Java 8, 11, and 17[1].

2. Spark 4.0, which is expected to be released soon, will likely support Java 17 and 21[3].

3. There is ongoing work to add support for newer Java versions in Spark:

   - Spark 3.3.x series is working on adding support for JDK 22[2].
   - There are efforts to build and run Spark on Java 21, which is targeted for Spark 4.0.0[4].

4. As of now, there is no mention of official support for JDK 23 in Spark.

It's important to note that JDK 23 introduces changes related to the Security Manager that may affect Spark's functionality[5]. Specifically:

- The `Subject.getSubject` API now requires allowing the Security Manager.
- Applications using this API may need to set the system property `java.security.manager=allow` as a temporary workaround.

Given these factors, it's unlikely that Spark currently supports JDK 23 out of the box. Users wanting to use Spark with JDK 23 may encounter compatibility issues and might need to apply workarounds or wait for official support in future Spark releases.

For the most up-to-date and stable usage, it's recommended to use Spark with the Java versions officially supported for your specific Spark version.

Citations:
[1] https://community.cloudera.com/t5/Community-Articles/Spark-and-Java-versions-Supportability-Matrix/ta-p/383669
[2] https://docs.scala-lang.org/overviews/jdk-compatibility/overview.html
[3] https://github.com/OpenLineage/OpenLineage/issues/2818
[4] https://issues.apache.org/jira/browse/SPARK-43831
[5] https://inside.java/2024/07/08/quality-heads-up/
[6] https://github.com/quarkusio/quarkus/issues/39634
[7] https://stackoverflow.com/questions/76431897/which-jdk-to-use-with-spark
[8] https://openjdk.org/jeps/486

