# psiml2021
My implementation of PSIML 2021 homework done on petlja.org

It is done as a hackathon project so it may not be in the best shape until I fix it at some point in the future.

These are mine explenations of the problems that will stay here until Homework Organizers decide to publish original Homework with all details.

### main.py

Implementation of the TF-IDF problem. It is constructed of getting stem for every word and then calculating TF value for every stem.
After that, we calculate IDF value by looking at occurances of this stem in all other documents.

At the end we multiply those values and use them to print the 5 most important sentences in the document.


### treci.py

Here we are given 4 values: N, P, S and T.

N - number of points/particles
S - size of a square going from -S to S
T - units of time
P - probability of vanishing ov every particle when it hits the wall

We are also given starting positions and velocities of particles and we should calculate where each one of them will be in T units of time.
We kept in mind that every time a particle hits a wall it bounces back in the way that the out-angle is the same as the in-angle.

### cetvrti.py

We are given a image of some chess regular chess position as well as the set of images of all black and white pieces and black and white board tiles.
We should return the FEM string describing exact chess position, as well a calculation if the Black/White is giving a check, and if there is a check, 
we calculated if that check is a mate. 
