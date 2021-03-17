import math
import copy

S = 0
N = 0
T = 0
P = 0
particles = []
particles2 = []
distances_from_center = []
collisions = {}


def avg(xs):
    if len(xs) == 0:
        return 0.0
    return sum(xs) / len(xs)


def distance_from_center(p):
    px = p[0]
    py = p[1]
    return math.sqrt(px * px + py * py)


def move_all_particles_backwards():
    move_all_particles_forward(direction=-1)


def particle_in_square(particle):
    x = particle[0]
    y = particle[1]

    if -S >= x or x >= S or S <= y or y <= -S:
        return False
    return True


def fix_p_back_inside(p):
    if particle_in_square(p):
        return p

    num_of_collisions = 0

    while not particle_in_square(p):
        if p[0] >= S:
            p[0] -= 2 * (p[0] - S)
            p[2] *= -1
            num_of_collisions += 1
        if p[0] <= -S:
            p[0] += 2 * (-S - p[0])
            p[2] *= -1
            num_of_collisions += 1
        if p[1] >= S:
            p[1] -= 2 * (p[1] - S)
            p[3] *= -1
            num_of_collisions += 1
        if p[1] <= -S:
            p[1] += 2 * (-S - p[1])
            p[3] *= -1
            num_of_collisions += 1

    return p, num_of_collisions


def particle_X_position_out_of_range(p):
    if p[0] >= S or p[0] <= -S:
        return True
    return False


def move_all_particles_forward(direction=1):
    collisions_this_time = 0
    p_id = 0
    for p in particles:
        p[0] += p[2] * direction
        p[1] += p[3] * direction

        if not particle_in_square(p):
            p, p_collisions = fix_p_back_inside(p)
            collisions_this_time += p_collisions
            collisions[p_id] += p_collisions

        p_id += 1
    update_distances_from_center()
    return collisions_this_time


def load_data():
    NSTP = input().split(' ')
    global S
    global N
    global T
    global P
    N = int(NSTP[0])
    S = int(NSTP[1])
    T = int(NSTP[2])
    P = float(NSTP[3])

    assert len(particles) == 0

    for i in range(N):
        particles.append(list(map(float, input().split(' '))))

    global particles2
    particles2 = copy.deepcopy(particles)

    global collisions
    for p_id in range(N):
        collisions[p_id] = 0

    update_distances_from_center()


def update_distances_from_center():
    global distances_from_center
    distances_from_center = []
    for p in particles:
        distances_from_center.append(distance_from_center(p))


def print_coos():
    print('\n--------------')
    print('S = ', S)
    print('- - - - - - - ')
    for p in particles:
        print(p[0], p[1], p[2], p[3])
    print('--------------')
    print('avg = ', avg(distances_from_center))
    print('--------------\n')


def calculate_moment_of_big_bang():
    avg_dist = avg(distances_from_center)
    desc = True

    counter = 0
    while desc:
        move_all_particles_backwards()
        # print_coos()
        new_avg = avg(distances_from_center)
        desc = new_avg < avg_dist
        avg_dist = new_avg
        counter += 1

    restore_particles()
    return counter - 1


def restore_particles():
    global particles
    global distances_from_center
    particles = copy.deepcopy(particles2)
    distances_from_center = []


def calculate_num_of_collisions():
    restore_particles()
    counter = 0
    for t in range(T):
        counter += move_all_particles_forward()

    restore_particles()
    return counter


def calculate_expected_num_of_particles():
    global collisions
    global N
    global P

    probs = []
    for n in range(N):
        probs.append(collisions[n])

    probs = list(map(lambda p: P**p, probs))
    return sum(probs)


if __name__ == '__main__':
    load_data()
    print(calculate_moment_of_big_bang(), calculate_num_of_collisions(), calculate_expected_num_of_particles())
