import matplotlib.pyplot as plt

plt.ion()
for i in range(100):
    x = range(i)
    y = range(i)
    # plt.gca().cla() # optionally clear axes
    plt.plot(x, y)
    plt.title(str(i))
    plt.draw()
    plt.pause(0.1)

print('what?')
#plt.show(block=True) # block=True lets the window stay open at the end of the animation.