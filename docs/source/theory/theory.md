# Theory
In this section we illustrate the implemented algorithm for solving the one dimensional cutting stock problem.
This algorithm is based on the column generation technique of mathematical programming and is **Not Exact**.

Number of possible cutting patterns grows by the order of factorial against number of needed lengths So generating all the possible patterns beforehand is not a practical solution. The designed algorithm is based on the idea of generating the patterns by need. The parent model decides how many of each of the patterns is needed to be cut. Based on the optimal solution of the parent model in each iteration, the child model is formed and its optimal solution determines whether the termination condition is satisfied or should be continued and returns a new pattern. The pattern generated in the child model will definitely improve the parrent's solution.


This technique is named column generation, because in each iteration a new variable(forms a column in the coefficient matrix) is introduced to the parent model.
The extracted data from the optimal solution of the parent model is the optimal value of the dual variables.
In the next sections, parent and child models are explained.

## Parent Model
The parent model determines that how many bars should be cut from each pattern to generate the needed pieces.

### Sets
- $I$ : set of patterns
- $J$ : set of needed pieces
- $L$ : set of needed lengths

### Variables
- $x_i$ : number of bars, cut based on pattern $i \in I$ 

### Parameters
- $a_{ij}$ : number of the piece $j \in J$ within the pattern $i \in I$
- $b_j$ : the number needed from piece $j \in J$
- $c_i$ : length of the pattern $i \in I$ 's bar
- $n_l$ : number of available bars of length $l \in L$


$$
   \begin{align}
   \min \quad &\sum_{i\in I}x_i l_i\\
    s.t.\quad &\sum_{i \in I} a_{ij} x_i \geq b_j ,\quad \forall j \in J &(1)\\
    \quad & \sum_{i \in \{i : c_i =l\}} x_i \leq n_l ,\quad \forall l \in L &(2)\\
    \quad & x_i \in  \mathbb{R}_+, \quad \forall i \in I\\
   \end{align}
$$
The Objective function minimized the whole length of the used bars.
Constraint (1) ensures that all the needed pieces are generated.
Constraint (2) limits the number of used bars with a specific length.



## Child Model
This model is an integer knapsack problem. The coefficients of the objective function are the optimal value of the dual variables of parernt model. 
### Variables
- $z_j$ : Integer variable indicating number of pieces of length $j \in J$ in the pattern
- $w$ : Binary variable indicating whether the pattern has a waste or not
- $s$ : slack variable
### Parameters
- $l_j$ : length of the piece $j \in J$
- $BW$ : blade's width
- $B_\max$ : maximum number of blades

The optimal value of the objective function determines if the optimality condition is satisfied or not.
If $\nu^* - L <= 0$ optimality condition of the algorithm is satisfied and terminates. Otherwise, a new pattern is generated to be added to the parent model.

$$
   \begin{align}
   \nu^*  = \min \quad &\sum_{j\in J}z_j u_j\\
    s.t.\quad &\sum_{j \in J} z_j l_j = L - s - \bigg( \big( \sum_{j \in J} z_j \big) -1 + w \bigg)BW  &(1)\\
    \quad & \sum_{j \in J} z_j \leq B_{\max} + 1 - w &(2)\\
    \quad & s/L \leq w \leq s &(3)\\
    \quad & z_j \in , \quad j \in \mathbb{Z}_+\\
    \quad & w \in \{0,1\}
   \end{align}
$$

Coefficient $u_j$ in the objective function, is the optimal value of the dual variable corresponding to the constraint (1) in the parent model.
Constraint (1) doesn't allow the pattern's pieces' length exceed the bar's length. It also considers the blade's width and determines the slack value.
Constraint (2) limits the number of blades in the pattern. Constraint (3) holds the logical condition "variable $w$ is equal to one iff slack variable $s$ is greater than zero".


### Final Model 
When the optimality condition is satisfied and the algorithm terminates, to get an interegr feasible solution we have to solve the parent model with some slight modifications. In order to satisfy the integrality condition, domain of the variable $x$ is changed to $\mathbb{Z}_+$. Some additional constraints can be considered in this stage.

### Variables
- $y_i$ : binary variable indicating whether the pattern $i \in I$ has been used or not

### Parameters
- $P_\max$ : maximum number of the used patterns

$$
   \begin{align}
   \min \quad &\sum_{i\in I}x_i l_i\\
    s.t.\quad &\sum_{i \in I} a_{ij} x_i \geq b_j ,\quad \forall j \in J &(1)\\
    \quad & \sum_{i \in \{i : l_i =l\}} x_i \leq n_l ,\quad \forall l \in L &(2)\\
    \quad &  x_i \leq y_i \bigg( \max \bigg\{ b_j/a_{ij}: a_{ij} > 0 , \forall j \in J \bigg\} \bigg) ,\quad \forall i \in I &(3)\\
    \quad & \sum_{i \in I} y_i \leq P_{\max} &(4)\\
    \quad & x_i \in  \mathbb{Z}_+, \quad \forall i \in I\\
    \quad & y_i \in \{0,1\}, \quad \forall i \in I
   \end{align}
$$
constraint (3) forces $y_i$ to be equal to one if the pattern $i \in I$ is used. The coefficient in the right-hand side is an upper bound for $x_i$ in the optimal solution.
Constraint (4) limits the number of used patterns.
