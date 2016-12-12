
## Diameter Algorithm Scrap
------------------
    References:
        https://www.cse.unsw.edu.au/~sergeg/papers/FratiGGM13isaac.pdf
        http://www.cis.upenn.edu/~sanjeev/papers/diameter.pdf
        http://dl.acm.org/citation.cfm?id=2953882

    Notes:
        We are given a graph G = (V, E) with an edge weight function w, an edge
        cost function c, an a maximum cost B.

        The goal is to find a set of candidate non-edges F.

        Let x[e] in {0, 1} denote if a non-edge e is excluded or included.

        minimize sum(c(e) * x[e] for e in F)
        such that
        weighted_diamter(graph.union({e for e in F if x[e]})) <= B

        There is a 4-Approximation of the BCMD problem
        Running time is O((3 ** B * B ** 3 + n + log(B * n)) * B * n ** 2)

        This algorithm usexs a clustering approach to find a set C, of B + 1
        cluster centers.  Then we create a minimum height rooted tree, T = (U
        \subseteq V, D) so that C \subseteq U.  This tree T approximates an
        optimal B-augmentation.

* Within each CC (using only reviewed edges) we want to add edges to ensure the
  diameter of each CC is no more than D.
* We want to choose a only a small number of edges that satisfy this
  constraint. We also want these edges to be comparable.
* Framed as (Bounded Cost Minimum Diameter Augmentation) diameter augmentation.
* https://www.cse.unsw.edu.au/~sergeg/papers/FratiGGM13isaac.pdf
* (BICONNECTIVITY AUGMENTION UNDER DIAMETER CONSTRAINTS)


* Augmenting trees to meet biconnectivity and diameter constraints ...
* We restrict ourselves to the unit cost, unit weight case for now. 
* Let G=(V, E) be the set of edges in the CC. 
* Let ~E be the compliment set of edges 
* We want to choose the lowest cost set of edges F ⊆ ~E such that diameter((V, E ∪ F)) <= D
* Diameter augmentation is NP hard. 
* Baseline greedy algorithm. 
* At each step add the edge with the lowest cost that decreases the diameter
  the most until a feasible D-Augmentation is achieved.


**"Designing Networks with Bounded Pairwise Distance"** by Yevgeniy Dodis and
Sanjeev Khanna (1999) (http://www.cis.upenn.edu/~sanjeev/papers/diameter.pdf) has the
correct problem and an approximation algorithm.

Given: 
Graph G = (V, E)
Candidate edges ~E
Cost function on candidate edges, c(~E) -> Real+
Real number d

Goal: 
Find a minimum cost set of edges E' ⊆ ~E such that the
diameter (max dist between any two pairs of points) when 
we add them to the graph G'=(V, E ∪ F) is at most d. 

In the unit-cost unit-length case there is an approximation algorithm 
with approximation ratio O(log(n) * log(d)). (n=|V| + |E|).

Idea is to create an LP-relaxation of the **Hitting Set** problem, find the
fractional solution, and apply randomized rounding (or a greedy solution) to
make the solution integral.

Actually what we do is solve the **restricted diameter-d** problem instead. 
However, it turns out that solving this is the same thing as solving **diameter-d**.
The restriction is that any path created between two points must use either 
exactly one edge in E' (type A) or exactly two consecutive edges incident on a
node s (type-B).


**NOTATION**

Let `U_d(G) = {u, v | dist(u, v) > d}` be unsatisfied pairs
Ⲅ(u,v) is the path between u and v in G'

* Let ~N(s) = {z for (s, z) in ~E if z != s} are vertices in G not connected to s.
* Define the nodes that are not connected to s and exactly distance i away from u in G.
`Layer_i(u) = ~N(s).isect({w for w in V if dist(u, w, G) == i})`
Then define the nodes that are not connected to s and within a distance i away from u in G.
  `LayerLeq_j(u) = union(Layer_i(u) for i in range(i + 1))`

* Let f[e] indicates if an edge e in ~E is chosen. 
Let x[w] = f[(s, w)]
For each (u, v) in `U_d(G)`, γ[(u, v)] = 1 indicates that an edge is covered by a type-A path. 
 γ[(u, v)] = 0 indicates it is a type-B path.

**Type-A Path Constraints**
`for e in U_d(G)` Add constraint `sum(f[e] > γ[e] for e in S[u, v])`
This indicates an edge is covered by a type A path. 

**Type-B Path Constraints**
type b paths have the form `u ~> y -> s -> z ~> v`. 
Where y in Layer_i(u) and z in Layer_l(v) and i + l <= (d-2)

An [i,j] path is one where y is at distance i from u and z is at distance d - 2 - j from v, and
if we add edges (s, y) and (s, z) to E then u and v are at distance d - j + i.

DEFINE:
`L_i(u) = sum(x[y] for y in Layer_i[u])`
`R_j(u) = sum(x[z] for y in Layer_{d - 2 - j}(v))` (mistake y for z?)
`R_j(u) = sum(x[z] for z in Layer_{d - 2 - j}(v))` (mistake y for z?)

Abbreviate:
`L_A = sum(L_i for i in A)`
`R_B = sum(L_j for j in B)`

`Some [i,j]-path selected for i in A and j in B <==> (min(L_A(u), R_B(v)} > = 1)`

Define 
`delta[(alpha, u, v)] = min(L_A[elpha](u), R_B[alpha](v))`

**The ILP**
```python

prob = pulp.LpProblem("restricted diameter-d relaxation", pulp.LpMinimize)
f = pulp.LpVariable.dicts(name='f', indexs=indexs, lowBound=0, upBound=1, cat=pulp.LpContinuous)
x = pulp.LpVariable.dicts(name='x', indexs=indexs, lowBound=0, upBound=1, cat=pulp.LpContinuous)

# Minimize the number of edges added
prob.objective = (
    sum(f[e] for e in ~E)
)

for (u, v) in U_d(G):
    # Ensure Type-A edges
    prob.add(
        sum(f[e] >= gamma[(u, v)] for e in S[(u, v)])
    )

For s in V:
    for w in ~N(s):
        prob.add(f[s, w] == x[w])

for (u, v) in U_d(G):
    for alpha in range(1, t + 1):
        # Ensure Type-B edges
        prob.add(
            delta[(alpha, u, v)] <= min(L_A[elpha](u), R_B[alpha](v))
        )
        # (u, v) must be covered by either a Type-A or Type-B path
        prob.add(
            sum(delta[(alpha, u, v)] >= 1 - gamma[u, v]
                for alpha in range(1, t + 1))
        )

```

Given a C-covering family F, the randomized rounding procedure is to include
`e` with probability `min(1, 9 * C * f[e] * log(n))`


As hitting set:
The universe S=~E.
For each pair (u, v) in U_d(G) add the following subsets to C.
If gamma[u,v] >= 1/3 add the set A = S[u, v].
If gamma[u,v] < 1/3 add two sets:
`A' = [e | e = (s, y) for y in Layer_LQi0(u)] and `
`B' = [e | e = (s, z) where z in LayerLeq(d - 2 - i0)(v)]`
( find i0 in [0, d-2] by solving eqn 7...
  1/(3C) <= min(sum(x[y] for y in LayerLeqi0(u)),
                sum(x[z] for y in LayerLeqi(d - 2 - i0)(v)))
)


**Hitting Set** is equivalent to set cover and solutions by trivial conversions.
Given: Collection C of subsets of a finite set S.
Goal: The hitting set for C is a subset S' \subeq S s.t. S' contains at least
one element from each subset in C. Then use greedy algorithm by iteratively 
picking edges that hit the largest number of sets among those yet untouched. 


**Min-cost d-Spanner** problem is to find a min cost set of
edges E'⊆ E (note note ~E) s.t. Each pair of vertices is at most a factor d
further apart in G'=(V, E') than it was in G. 
An (α,β)-approximation relaxes the distance bound and cost bound respectively.
