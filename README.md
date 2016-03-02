# Real-time data collection for IDEs
## Description
Integrated development environments (IDEs) have been around for a few decades already, yet none of the modern IDEs was 
able to successfully integrate their source code editors with the actual data stream flowing though the code. Ability to 
display the actual data running through the system promises many potential benefits, including easier debugging and code 
recall, which results in significantly lower code maintenance costs.
The goal of this project is to design a proof-of-concept system in one programming language that allows full code 
instrumentation (like Python). This system should be able to seamlessly capture all values for all variables in source 
code and store them somewhere, with further possibility to easily retrieve saved values. The system should also provide 
an API to the storage in order to make the data accessible for navigation and display in third-party applications.

## Specification and scope of the project

### Database
* The used database engine is MongoDB
* The database will be seperated in two parts : user information for the interface and data from the runs
* During the project different ways of storing the variables have to be tried in order to optimize the database in terms
of space and time
  * Should the collections be user centered or file centered ?
* Entries from the runs will contain the following identifiers :
  * a git commit identifier and a timestamp
  * a identifier for the author of the run
  * a identifier to know from which file the run is.

### Software
* Use the Mongoengine
* Extend the actual code to include more objects. (Low priority)
* Establish a connection with the git repository to get the commit identifier.
* Inner classes.
* Loops :
  1. Inter-function navigation in the loop
  2. Variable storing techniques : full, sample (then what size ?), ranges (if applicable), other ?
  3. Conditions --> proportion of execution times (how often?)
  4. Ability to plot values distribution for a specified variable in aggregations.

### Interface
* Develop an interface in HTML/Python in order to visualize the results.
* The framework "Flask" will be used to develop the interface
* In this interface th euser should have at least these possibilites :
  * Filter the diferent runs by date, commit identifier and author of the run
  * Delete a run
* The user should be able to open at least two different runs in order to be able to compare them.

### Experiments
  * Detailed workflow on experiments
