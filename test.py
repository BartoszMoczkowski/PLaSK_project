import plask 
import numpy as np
import matplotlib.pyplot as plt

efm = 0

##Materials

@plask.material.simple("GaAs")
class GaAs_my(plask.material.Material):
    pass
    #override functions



##geometry
root = plask.geometry.Stack2D()

layer1 = plask.geometry.Block2D(10,0.07,"GaAs")
root.prepend(layer1)

bragg_mirrors_1 = plask.geometry.Stack2D(repeat=24)

mirror_layer1 = plask.geometry.Block2D(10,0.0795,"Al(0.73)GaAs")
bragg_mirrors_1.prepend(mirror_layer1)
mirror_layer2 = plask.geometry.Block2D(10,0.07,"GaAs")
bragg_mirrors_1.prepend(mirror_layer2)

root.prepend(bragg_mirrors_1)

cavity_region = plask.geometry.Shelf()
cavity_layer1 = plask.geometry.Block2D(4,0.016,"AlAs")
cavity_region.prepend(cavity_layer1)
cavity_layer2 = plask.geometry.Block2D(6,0.016,"AlOx")
cavity_region.prepend(cavity_layer2)

root.prepend(cavity_region)
cavity_layer3 = plask.geometry.Block2D(10,0.0635,"Al(0.73)GaAs")
root.prepend(cavity_layer3)
cavity_layer4 = plask.geometry.Block2D(10,0.1376,"GaAs")
root.prepend(cavity_layer4)

gain_region = plask.geometry.Shelf()
gain_layer1 = plask.geometry.Block2D(4,0.016,"AlAs")
gain_region.prepend(cavity_layer1)
gain_layer2 = plask.geometry.Block2D(6,0.016,"AlOx")
gain_region.prepend(cavity_layer2)






plask.loadxpl("tutorial2.xpl")



cylindrical_space = plask.geometry.Cylindrical(root,outer = "extend",bottom="GaAs")



efm.inGain = 4000
mn = efm.find_mode(980.,m=0)

loss = - efm.modes[mn].lam.imag



lams = np.linspace(900,980,1601)
dets = abs(efm.get_determinant(lams, m=0))
dets_filtered_left = -dets[1:-1] + dets[:-2]
dets_filtered_right = -dets[1:-1] + dets[2:]
dets_filtered =np.bitwise_and( (dets_filtered_left > 0),  (dets_filtered_right > 0))
lam_modes = lams[1:-1][dets_filtered]
print(lam_modes)


plt.plot(lams,dets)
plt.show()


chosen_lam_start_points = np.random.choice(lam_modes, 3)



for m in range(0,3):

    plt.figure()
    plt.title(f"m = {m}")
    plt.axvline(4., color='k',lw=0.7)
    plt.axhline(0.,color='k',lw=1)
    plt.xlim(0.,4.)
        
    for lam_start_point in chosen_lam_start_points:
        
        try: 
            mn = efm.find_mode(lam_start_point,m=m)
        except:
            
            print(f"failed to reach a solution for lam = {lam_start_point}, m = {m}")
        magr = efm.outLightMagnitude(mn,MSH.plotr)
        magr /= max(magr)
        plask.plot_profile(magr,label = f"l = {lam_start_point}")
        
    plt.legend()

    
plt.show()
