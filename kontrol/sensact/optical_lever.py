"""Optical lever sensing matrix
"""
import numpy as np

import kontrol


class OpticalLeverSensingMatrix(kontrol.SensingMatrix):  # Too long?
    r"""Optical lever sensing matrix base class.

    This is a sensing matrix that maps tilt-sensing QPD and
    length-sensing QPD (placed behind a lens) readouts to
    the suspended optics' longitudinal, pitch, and yaw displacements.

    Parameters
    ----------
    r_h: float
        Lever arm from the optics to the tilt-sensing QPD plane on the
        horizontal plane (amplifying yaw).
    r_v: float
        Lever arm from the optics to the tilt-sensing QPD plane on the
        vertical plane (amplifying pitch).
    alpha_h: float
        Angle of incidence on the horizontal plane.
    alpha_v: float
        Angle of incidence on the vertical plane.
    r_lens_h: float, optional
        Lever arm from optics to the lens on the horizontal plane.
        Defaults None. Specify if it exists.
    r_lens_v: float, optional
        Lever arm from optics to the lens on the vertical plane.
        Defaults None. Specify if it exists.
    d_h: float, optional
        Horizontal distance from the lens to the length-sensing QPD.
        Defaults None.
    d_v: float, optional
        Vertical distance from the lens to the length-sensing QPD.
        Defaults None.
    delta_x: float, optional
        Horizontal miscentering of the beam spot at the optics plane.
    delta_y: float, optional
        Vertical miscentering of the beam spot at the optics plane.
    phi_tilt: float, optional
        Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
        Defaults None.
    phi_len: float, optional
        Angle from the length-sensing QPD frame to the yaw-pitch frame.
        Defaults None.
    f: float, optional
        Focal length of the convex lens.
        Defaults None.
    format: str, optional
        Format of the sensing matrix.
        Choose from
            "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                and output (longitudinal, pitch and yaw).
            "xy": Matrix as shown in [1]_.

    Notes
    -----
    We're using equation (29) from [1]_.

    .. math::
        \begin{pmatrix}
            x_L\\
            \theta_P\\
            \theta_Y
        \end{pmatrix}
        =
        \mathbf{C}_\mathrm{miscenter}
        \mathbf{C}_\mathrm{align}
        \mathbf{C}_\mathrm{rotation}
        \begin{pmatrix}
            x_\mathrm{tilt}\\
            y_\mathrm{tilt}\\
            x_\mathrm{len}\\
            y_\mathrm{len}
        \end{pmatrix},

    where :math:`x_L` is the longitudinal displacement of the optics,
    :math:`\theta_P` is the pitch angular displacement of the optics,
    :math:`\theta_Y` is the yaw angular displacement of the optics,
    :math:`x_\mathrm{tilt}` is the horizontal displacement of the beam spot
    at the tilt-sensing QPD plane,
    :math:`y_\mathrm{tilt}` is the vertical displacement of the beam spot
    at the tilt-sensing QPD plane,
    :math:`x_\mathrm{len}` is the horizontal displacement of the beam spot
    at the length-sensing QPD plane,
    :math:`y_\mathrm{len}` is the vertical displacement of the beam spot
    at the length-sensing QPD plane,

    .. math::
        \mathbf{C}_\mathrm{rotation}
        =
        \begin{bmatrix}
            \cos\phi_\mathrm{tilt} & \sin\phi_\mathrm{tilt} & 0 & 0\\
            -\sin\phi_\mathrm{tilt} & \cos\phi_\mathrm{tilt} & 0 & 0\\
            0 & 0 & \cos\phi_\mathrm{len} & \sin\phi_\mathrm{len}\\
            0 & 0 & -\sin\phi_\mathrm{len} & \cos\phi_\mathrm{len}
        \end{bmatrix},

    .. math::
        \mathbf{C}_\mathrm{align}
        =
        \begin{bmatrix}
            2\sin\alpha_h & 0 & 2r_h\\
            2\sin\alpha_v & 2r_v & 0\\
            2\sin\alpha_h\left(1-\frac{d_h}{f}\right) & 0 &
            2\left[\left(1-\frac{d_h}{f}\right)r_{\mathrm{lens},h}+d_h\right]\\
            2\sin\alpha_v\left(1-\frac{d_v}{f}\right) &
            2\left[\left(1-\frac{d_v}{f}\right)r_{\mathrm{lens},v}+d_v\right]
            & 0\\
        \end{bmatrix}^{+},

    .. math::
        \mathbf{C}_\mathrm{miscenter}
        =
        \begin{bmatrix}
            1 & \delta_y & \delta_x\\
            0 & 1 & 0\\
            0 & 0 & 1
        \end{bmatrix}^{-1},

    :math:`\phi_\mathrm{tilt}` is the angle between the tilt-sensing QPD
    and the yaw-pitch frame, :math:`\phi_\mathrm{len}` is the angle between
    the length-sensing QPD and the yaw-pitch frame,
    :math:`r_h` is the lever arm on the horzontal plane, :math:`r_v` is the
    lever arm on the vertical plane,
    :math:`\alpha_h` is the angle of incidence on the horizontal plane,
    :math:`\alpha_v` is the angle of incidence on the vertical plane,
    :math:`r_{\mathrm{lens}, h}` is the lever arm between the optics
    and the lens on the horizontal plane,
    :math:`r_{\mathrm{lens}, v}` is the lever arm between the optics and the
    lens on the vertical plane,
    :math:`d_h` is the distance between the lens and the length-sensing QPD
    on the horizontal plane,
    :math:`d_v` is the distance between lens and the length-sensing QPD
    on the vertical plane,
    and :math:`f` is the focal length of the convex lens.

    References
    ----------
    .. [1]
        Tsang Terrence Tak Lun,
        Sensing Matrices for Optical Levers of the KAGRA Main Optics,
        https://github.com/terrencetec/kagra-optical-lever.
    """
    def __new__(cls, r_h, r_v, alpha_h, alpha_v,
                 r_lens_h=0, r_lens_v=0, d_h=0, d_v=0,
                 delta_x=0, delta_y=0,
                 phi_tilt=0, phi_len=0, f=np.inf,
                 format="OPLEV2EUL"):
        """Constructor

        Parameters
        ----------
        r_h: float
            Lever arm from the optics to the tilt-sensing QPD plane on the
            horizontal plane (amplifying yaw).
        r_v: float
            Lever arm from the optics to the tilt-sensing QPD plane on the
            vertical plane (amplifying pitch).
        alpha_h: float
            Angle of incidence on the horizontal plane.
        alpha_v: float
            Angle of incidence on the vertical plane.
        r_lens_h: float, optional
            Lever arm from optics to the lens on the horizontal plane.
            Defaults None. Specify if it exists.
        r_lens_v: float, optional
            Lever arm from optics to the lens on the vertical plane.
            Defaults None. Specify if it exists.
        d_h: float, optional
            Horizontal distance from the lens to the length-sensing QPD.
            Defaults None.
        d_v: float, optional
            Vertical distance from the lens to the length-sensing QPD.
            Defaults None.
        delta_x: float, optional
            Horizontal miscentering of the beam spot at the optics plane.
        delta_y: float, optional
            Vertical miscentering of the beam spot at the optics plane.
        phi_tilt: float, optional
            Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
            Defaults None.
        phi_len: float, optional
            Angle from the length-sensing QPD frame to the yaw-pitch frame.
            Defaults None.
        f: float, optional
            Focal length of the convex lens.
            Defaults None.
        format: str, optional
            Format of the sensing matrix.
            Choose from
                "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                    with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                    and output (longitudinal, pitch and yaw).
                "xy": Matrix as shown in [1]_.

        References
        ----------
        .. [1]
            Tsang Terrence Tak Lun,
            Sensing Matrices for Optical Levers of the KAGRA Main Optics,
            https://github.com/terrencetec/kagra-optical-lever.
        """
        c_align_inv = np.array([
        [2*np.sin(alpha_h), 0, 2*r_h],
        [2*np.sin(alpha_v), 2*r_v, 0],
        [2*np.sin(alpha_h) * (1-d_h/f), 0, 2*((1-d_h/f)*r_lens_h + d_h)],
        [2*np.sin(alpha_v) * (1-d_v/f), 2*((1-d_v/f)*r_lens_v + d_v), 0]
        ])
        c_align = np.linalg.pinv(c_align_inv)

        c_rotation = np.array([
        [np.cos(phi_tilt), np.sin(phi_tilt), 0, 0],
        [-np.sin(phi_tilt), np.cos(phi_tilt), 0, 0],
        [0, 0, np.cos(phi_len), np.sin(phi_len)],
        [0, 0, -np.sin(phi_len), np.cos(phi_len)]
        ])

        c_miscenter_inv = np.array([
        [1, delta_y, delta_x],
        [0, 1, 0],
        [0, 0, 1]
        ])
        c_miscenter = np.linalg.inv(c_miscenter_inv)
        c_sensing = c_miscenter @ c_align @ c_rotation
        obj = super(OpticalLeverSensingMatrix, cls).__new__(cls, matrix=c_sensing)
        return obj
