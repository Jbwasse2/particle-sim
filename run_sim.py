from backend import *

# initialize simulation
system = System()
backend = WBallBackend(system)
simulation = Simulation(backend)
# We will execute the callback every step
simulation.add(cbk, 1, db=pos_db)

# create N particles at random locations in the box
for i in range(N):
    x,y = L*random(), L*random()
    vel = np.array([random()-0.5, random()-0.5])
    norm = np.linalg.norm(vel)
    vel /= norm
    system.particle.append(Particle(position=[x,y], velocity=list(vel), radius = None, species= 'A-free'))

# run simulation for T steps
simulation.run(T-1)

print("ran sim for ",T,"steps")

# write data to file
with open(simname+'.xyz','w') as th:
    for i in range(T):
        xys = pos_db[i]
        for (_, [x,y]) in xys:
            th.write(str(x)+" "+str(y)+" ")
        th.write("\n")

print("wrote data to",simname+".xyz")
print("writing video to",simname+".mp4")

class Data:

    def __init__(self, db, start=0):
        self.db = db
        self.num = start

    def __iter__(self):
        return self

    def clean_system(self, dat):
        types = [t for (t,xy) in dat]
        xys = [xy for (t,xy) in dat]
        return types, np.array(xys)

    def __next__(self):
        dat = self.db[self.num]
        self.num += 1
        return self.clean_system(dat)

d = Data(pos_db)

color_map = { 'A-wall': (0, 0, 1)
            , 'A-free': (0, 0, 1)
            , 'B-wall': (0, 1, 0)
            , 'B-free': (0, 1, 0)
            }
size_map =  { 'A-wall': 10
            , 'A-free': 10
            , 'B-wall': 50
            , 'B-free': 50
            }

particles = np.zeros(N, dtype=[('position', float, 2),
                               ('size',     float, 1),
                               ('color',    float, 3)])

init = copy(next(d))

particles['position'] = init[1]
particles['color'] = [color_map[t] for t in init[0]]
particles['size'] = [size_map[t] for t in init[0]]

fig = plt.figure()
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=(-0.2, L+0.2), ylim=(-0.2, L+0.2))

scat = ax.scatter(particles['position'][:,0]
                , particles['position'][:,1]
                , facecolors=particles['color']
                , s=particles['size']
                )

# rect is the box edge
rect = plt.Rectangle([0,0],
                     L,
                     L,
                     ec='none', lw=2, fc='none')
ax.add_patch(rect)

def init():
    """initialize animation"""
    global rect
    global scat
    rect.set_edgecolor('none')
    return scat, rect

def animate(i):
    """perform animation step"""
    global d, rect, dt, ax, fig, particles
    dat = next(d)

    # update pieces of the animation
    rect.set_edgecolor('k')
    scat.set_facecolors([color_map[t] for t in dat[0]])
    scat.set_sizes([size_map[t] for t in dat[0]])
    scat.set_offsets(dat[1])
    return scat, rect

ani = animation.FuncAnimation(fig, animate, frames=T-1,
                              interval=10, blit=True, init_func=init)


# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
ani.save(simname+'.mp4', fps=15, extra_args=['-vcodec', 'libx264'])