"""Matrix method algorithm for x-ray reflectivity and transmittivity as described by A. Gibaud and G. Vignaud in
J. Daillant, A. Gibaud (Eds.), "X-ray and Neutron Reflectivity: Principles and Applications", Lect. Notes Phys. 770
(Springler, Berlin Heidelberg 2009), DOI 10.1007/978-3-540-88588-7, chapter 3.2.1 "The Matrix Method".

Conventions used:
I'm following the conventions of A. Gibaud and G. Vignaud cited above:
There is a stack of j=0..N media on a substrate S, with j=0 and S being infinite. The interface between j and j+1
is Z_{j+1}, so Z_1 is the interface between the topmost layer (i.e. usually air or vacuum) and the first sample layer.
Electromagnetic waves are represented by their electric field \vec{E}, which is divided in one part travelling
downwards, \vec{E}^- and one travelling upwards, \vec{E}^+.

\vec{E}^{-/+} = A^{-/+} \exp\( +i(\omega t - k_{\text{in}x,j} x - k_\{\text{in}z,j} z) \) \, \hat{e}_y

The magnitude of the electric fields (which is time-independent) is denoted by:
U(-/+ k_{\text{in}z,j}, z) = A^{-/+}_j \exp(-/+ ik_{\text{in}z,j} z)

using
p_{j, j+1} = \frac{k_{z,j} + k_{z,j+1}}{2k_{z,j}}
m_{j, j+1} = \frac{k_{z,j} - k_{z,j+1}}{2k_{z,j}}

the refraction matrix \RR_{j, j+1} is given by:
 \( \begin{pmatrix}
  U(k_{z,j}, Z_{j+1}) \\
  U(-k_{z,j}, Z_{j+1})
 \end{pmatrix} \)
 =
 \( \begin{pmatrix}  % this is \RR_{j, j+1}
  p_{j, j+1} & m_{j, j+1} \\
  m_{j, j+1} & p_{j, j+1}
 \end{pmatrix} \)
 \( \begin{pmatrix}
  U(k_{z,j+1}, Z_{j+1}) \\
  U(-k_{z,j+1}, Z_{j+1})
 \end{pmatrix} \)

while the translation matrix \TT is defined as
 \( \begin{pmatrix}
  U(k_{z,j}, z) \\
  U(-k_{z,j}, z)
 \end{pmatrix} \)
 =
 \( \begin{pmatrix}  % this is \TT_{j}
  exp(-ik_{z,j} h) & 0 \\
  0 & exp(ik_{z,j} h)
 \end{pmatrix} \)
 \( \begin{pmatrix}
  U(k_{z,j}, z+h) \\
  U(-k_{z,j}, z+h)
 \end{pmatrix} \)

such that the transfer matrix \MM is
 \MM = \prod_{j=0}^N \( \RR_{j,j+1} \TT_{j+1} \) \RR_{N,s}
 =
 \( \begin{pmatrix}
  M_{11} & M_{12} \\
  M_{21} & M_{22}
 \end{pmatrix} \)

with this, the reflection coefficient is:
 r = \frac{M_{12}}{M_{22}}
and the transmission coefficient is:
 t = \frac{1}{M_{22}}

"""

import numpy as np
import scipy as sp


def reflec_and_trans(n, lam, theta, thick):
    """Calculate the reflection coefficient and the transmission coefficient for a stack of N layers, with the incident
    wave coming from layer 0, which is reflected into layer 0 and transmitted into layer N.
    Note that N=len(n) is the total number of layers, including the substrate. That is the only point where the notation
    differs from Gibaud & Vignaud.
    :param n: vector of refractive indices n = 1 - \delta - i \beta of all layers, so n[0] is usually 1.
    :param lam: x-ray wavelength in nm
    :param theta: incident angle in rad
    :param thick: thicknesses in nm, len(thick) = N-2, since layer 0 and layer N are assumed infinite
    :return: (reflec, trans)
    """
    # wavevectors in the different layers
    k = 2 * np.pi / lam  # k is conserved
    k_x = k * np.cos(theta)  # k_x is conserved due to snell's law
    k_z = -np.sqrt((k**2 * n**2) - k_x**2)  # k_z is different for each layer.

    # matrix elements of the refraction matrices
    # p[j] is p_{j, j+1}
    # p_1{j, j+1} = k_{z, j} + k_{z, j+1} / (2 * k_{z, j})  for all j=0..N-1
    p = (k_z[:-1] + k_z[1:]) / (2 * k_z[:-1])
    m = (k_z[:-1] - k_z[1:]) / (2 * k_z[:-1])

    RR = [np.matrix([[p[i], m[i]],
                     [m[i], p[i]]]) for i in range(len(p))]

    # matrix elements of the translation matrices
    w = 1j * k_z[1:-1] * thick
    TT = [np.matrix([[np.exp(-v), 0],
                     [0, np.exp(v)]]) for v in w]

    # the transfer matrix is obtained as
    # \RR_{0, 1} \prod_{j=1}^N-1 \TT_{j} \RR_{j, j+1}
    # with
    # \RR{j, j+1} = RR[j]
    # and
    # \TT{j} = T[j-1]
    MM = RR[0].copy()
    for R, T in zip(RR[1:], TT):
        MM *= T
        MM *= R

    # reflection coefficient
    r = MM[0, 1] / MM[1, 1]

    # transmission coefficient
    t = 1 / MM[1, 1]

    return (r, t)






if __name__ == '__main__':
    r, t = reflec_and_trans(np.array([1, 1-1e-5-1e-6j, 1-2e-5-2e-6j]), 0.15, 0.6, [100])
    print(r - (2.49952738449e-05-1.14399563324e-05j))
    print(t - (-0.872002220964+0.504602517288j))
    #reflec_and_trans(np.array([1, 1-1e-5-1e-6j, 1-2e-5-2e-6j]), 0.15, np.deg2rad([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]), [100])
    pass

















