import plask 
import optical # type: ignore pylace issue
import meta # type: ignore pylance issue
from meta import shockley
import numpy as np
import matplotlib.pyplot as plt

efm = 0

##Materials

@plask.material.simple("GaAs")
class GaAs_my(plask.material.Material):
    
    def nr(self, lam, T=300, n=0):

        return 3.42
        return super().nr(lam, T, n)

@plask.material.simple("semiconductor")
class Active(plask.material.Material):
    def nr(self, lam, T=300, n=0):
        return 3.53

    def absp(self, lam, T=300):
        return 0

@plask.material.simple("In(0.22)GaAs")
class InGaAsQW(plask.material.Material):
    def nr(self, lam, T=300, n=0):
        return 3.621

    def absp(self, lam, T=300):
        return 0
    
    def A(self, T=300):
        return 110000000
        return super().A(T)
    def B(self, T=300):
        return 7e-011-1.08e-12*(T-300)

    def C(self, T=300):
        return 1e-029+1.4764e-33*(T-300)
    def D(self, T=300):
        return 10+0.01667*(T-300)

@plask.material.simple("Active")
class Inactive(plask.material.Material):

    def absp(self, lam, T=300):
        return 1000

##geometry
root = plask.geometry.Stack2D()

#WHY ARE WE USING PREPEND IN THE TUTORIAL AAAAA

top_contact = plask.geometry.Shelf()
gap = plask.geometry.Block2D(6,0.05,"air")
n_contact = plask.geometry.Block2D(4,0.05,"Au")
top_contact.append(gap)
top_contact.append(n_contact)
root.prepend(top_contact)



layer1 = plask.geometry.Block2D(10,0.07,"GaAs:Si=2e+18")
root.prepend(layer1)

bragg_mirrors_1 = plask.geometry.Stack2D(repeat=24)

mirror_layer1 = plask.geometry.Block2D(10,0.0795,"Al(0.73)GaAs:Si=2e+18")
bragg_mirrors_1.prepend(mirror_layer1)
mirror_layer2 = plask.geometry.Block2D(10,0.07,"GaAs:Si=2e+18")
bragg_mirrors_1.prepend(mirror_layer2)

root.prepend(bragg_mirrors_1)

cavity_region = plask.geometry.Shelf()
cavity_layer1 = plask.geometry.Block2D(4,0.016,"AlAs:Si=2e+18")
cavity_layer2 = plask.geometry.Block2D(6,0.016,"AlOx")
cavity_region.prepend(cavity_layer2)
cavity_region.prepend(cavity_layer1)

root.prepend(cavity_region)

cavity_layer3 = plask.geometry.Block2D(10,0.0635,"Al(0.73)GaAs:Si=2e+18")
root.prepend(cavity_layer3)
cavity_layer4 = plask.geometry.Block2D(10,0.1160,"GaAs:Si=5e+17")
root.prepend(cavity_layer4)

gain_region = plask.geometry.Stack2D(repeat=4)
gain_region.role = "active"
qw = plask.geometry.Block2D(10,0.005,"InGaAsQW")
qw.role = "QW"
gain_region.prepend(qw)
gain_layer2 = plask.geometry.Block2D(10,0.005,"GaAs")
gain_region.prepend(gain_layer2)

root.prepend(gain_region)


bottom_gain = plask.geometry.Block2D(10,0.1160,"GaAs:C=5e+17")
root.prepend(bottom_gain)

bragg_mirrors_2 = plask.geometry.Stack2D(repeat=24)

mirror_layer2_1 = plask.geometry.Block2D(10,0.0795,"Al(0.73)GaAs:C=2e+18")
bragg_mirrors_2.prepend(mirror_layer2_1)
mirror_layer2_2 = plask.geometry.Block2D(10,0.07,"GaAs:C=2e+18")
bragg_mirrors_2.prepend(mirror_layer2_2)

root.prepend(bragg_mirrors_2)

p_contcat = plask.geometry.Block2D(5,5.,"GaAs:Si=2e+18")
root.prepend(p_contcat)


cylindrical_space = plask.geometry.Cylindrical(root,outer = "extend",bottom="GaAs")

efm = optical.EffectiveFrequencyCyl(name = "efm")
efm.lam0 = 970.
efm.geometry = cylindrical_space

thc = shockley.ThresholdSearchCyl(name = "THC")

#Meshes 

plot2d_axis0 = plask.mesh.Regular(0,8,801)
plot2d_axis1 = plask.mesh.Regular(-1,10,1101)
plot2d = plask.mesh.Rectangular2D(plot2d_axis0,plot2d_axis1)

plotr_axis0 = plask.mesh.Regular(0,12,1201)
plotr_axis1 = plask.mesh.Regular(4.625,4.625,1)
plotr = plask.mesh.Rectangular2D(plotr_axis0,plotr_axis1)

plotz_axis0 = plask.mesh.Regular(0.5,0.5,1)
plotz_axis1 = plask.mesh.Regular(-1,14,14001)
plotz = plask.mesh.Rectangular2D(plotz_axis0,plotz_axis1)



print(cylindrical_space.bbox)





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

   # plt.figure()
    #plt.title(f"m = {m}")
    #plt.axvline(4., color='k',lw=0.7)
   # plt.axhline(0.,color='k',lw=1)
    #plt.xlim(0.,4.)
        
    for lam_start_point in chosen_lam_start_points:
        
        try: 
            mn = efm.find_mode(lam_start_point,m=m)
        except:
            
            print(f"failed to reach a solution for lam = {lam_start_point}, m = {m}")
        magr = efm.outLightMagnitude(mn,plotr)
        magr /= max(magr)
        #plask.plot_profile(magr,label = f"l = {lam_start_point}")


        plask.figure()
        magz = efm.outLightMagnitude(mn,plotz)
        magz /= max(magz)
        plask.plot_profile(magz,color="C1")
        nrz = efm.outRefractiveIndex(plotz)
        plask.twinx()
        plask.plot_profile(nrz,color="blue")
        break

    plt.legend()

    
plt.show()
