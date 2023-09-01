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
    f_h : float, optional,
        Focal length of the lens projected to the horizontal plane.
        Defaults ``np.inf`` (no lens).
    f_v : float, optional,
        Focal length of the lens projected to the vertical plane.
        Defaults ``np.inf`` (no lens).
    format: str, optional
        Format of the sensing matrix.
        Choose from
            "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                and output (longitudinal, pitch and yaw).
            "xy": Matrix as shown in [1]_.
    coupling_matrix: array, optional
        The coupling matrix.
        Default None.

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
            2\sin\alpha_h\left(1-\frac{d_h}{f_h}\right) & 0 &
            2\left[\left(1-\frac{d_h}{f_h}\right)r_{\mathrm{lens},h}
            + d_h\right]\\
            2\sin\alpha_v\left(1-\frac{d_v}{f_v}\right) &
            2\left[\left(1-\frac{d_v}{f_v}\right)r_{\mathrm{lens},v}
            + d_v\right]
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
                phi_tilt=0, phi_len=0, f_h=np.inf, f_v=np.inf,
                format="OPLEV2EUL",
                coupling_matrix=None, *args, **kwargs):
        r"""Constructor

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
            Defaults 0.
        r_lens_v: float, optional
            Lever arm from optics to the lens on the vertical plane.
            Defaults 0.
        d_h: float, optional
            Horizontal distance from the lens to the length-sensing QPD.
            Defaults 0.
        d_v: float, optional
            Vertical distance from the lens to the length-sensing QPD.
            Defaults 0.
        delta_x: float, optional
            Horizontal miscentering of the beam spot at the optics plane.
            Defaults 0.
        delta_y: float, optional
            Vertical miscentering of the beam spot at the optics plane.
            Defaults 0.
        phi_tilt: float, optional
            Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
            Defaults 0.
        phi_len: float, optional
            Angle from the length-sensing QPD frame to the yaw-pitch frame.
            Defaults 0.
        f_h : float, optional,
            Focal length of the lens projected to the horizontal plane.
            Defaults ``np.inf`` (no lens).
        f_v : float, optional,
            Focal length of the lens projected to the vertical plane.
            Defaults ``np.inf`` (no lens).
        format: str, optional
            Format of the sensing matrix.
            Choose from
                "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                    with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                    and output (longitudinal, pitch and yaw).
                "xy": Matrix as shown in [1]_.
        coupling_matrix: array, optional
            The coupling matrix.
            Default None.

        Notes
        -----
        The coupling matrix has (i, j) elements as coupling ratios x_i/x_j.
        For example, consider the 2-sensor configuration:
        I have a coupled sensing readout :math:`x_{1,\mathrm{coupled}}`
        that reads :math:`x_{1,\mathrm{coupled}}=x_1 + 0.1x_2`.
        and, I have another coupled sensing readout
        :math:`x_{2,\mathrm{coupled}}` that reads
        :math:`x_{2,\mathrm{coupled}}=-0.2x_1 + x_2`.
        Then, the coupling matrix is

        .. math::
            \begin{bmatrix}
            1 & 0.1\\
            -0.2 & 1
            \end{bmatrix}.

        References
        ----------
        .. [1]
            Tsang Terrence Tak Lun,
            Sensing Matrices for Optical Levers of the KAGRA Main Optics,
            https://github.com/terrencetec/kagra-optical-lever.
        """
        # print("OpticalLeverSensingMatrix __new__")
        _c_align = c_align(
            r_h=r_h, r_v=r_v, alpha_h=alpha_h, alpha_v=alpha_v,
            r_lens_h=r_lens_h, r_lens_v=r_lens_v, d_h=d_h, d_v=d_v,
            f_h=f_h, f_v=f_v,
            **kwargs)
        _c_rotation = c_rotation(phi_tilt, phi_len)
        _c_miscenter = c_miscenter(delta_x, delta_y)

        c_sensing = _c_miscenter @ _c_align @ _c_rotation

        self = super(OpticalLeverSensingMatrix, cls).__new__(
            cls, matrix=c_sensing)  # __new__ in kontrol.sensact.matrix.Matrix
        super().__init__(self, matrix=None, coupling_matrix=coupling_matrix)
        self.c_align = _c_align
        self.c_rotation = _c_rotation
        self.c_miscenter = _c_miscenter
        self.c_sensing = c_sensing
        self.r_h = r_h
        self.r_v = r_v
        self.alpha_h = alpha_h
        self.alpha_v = alpha_v
        self.r_lens_h = r_lens_h
        self.r_lens_v = r_lens_v
        self.d_h = d_h
        self.d_v = d_v
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.phi_tilt = phi_tilt
        self.phi_len = phi_len
        self.f_h = f_h
        self.f_v = f_v
        self.format = format
        return self

    def __init__(self, *args, **kwargs):
        """Constructor
        """
        # print("OpticalLeverSensingMatrix __init__")
        # __init__ in kontrol.sensact.matrix.SensingMatrix
        # super().__init__(matrix=None, coupling_matrix=coupling_matrix)
        pass

    def update_matrices_decorator(func):
        """Update matrices and self upon setting new parameters.
        """
        def update_matrices(self, *args, **kwargs):
            func(self, *args, **kwargs)
            try:
                # print("In decorator")
                _c_align = c_align(
                    r_h=self.r_h, r_v=self.r_v,
                    alpha_h=self.alpha_h, alpha_v=self.alpha_v,
                    r_lens_h=self.r_lens_h, r_lens_v=self.r_lens_v,
                    d_h=self.d_h, d_v=self.d_v, f_h=self.f_h, f_v=self.f_v,
                    **kwargs)
                _c_rotation = c_rotation(self.phi_tilt, self.phi_len)
                _c_miscenter = c_miscenter(self.delta_x, self.delta_y)
                c_sensing = _c_miscenter @ _c_align @ _c_rotation
                if self.format in ["OPLEV2EUL", "OL2EUL"]:
                    c_sensing[:, [0, 1, 2, 3]] = c_sensing[:, [1, 0, 3, 2]]
                np.copyto(self, c_sensing)
            except AttributeError:
                pass
        return update_matrices

    @property
    def r_h(self):
        """Lever arm from optics to tilt-sensing QPD on the horizontal plane.
        """
        return self._r_h

    @r_h.setter
    @update_matrices_decorator
    def r_h(self, _r_h):
        """r_h setter.
        """
        self._r_h = _r_h

    @property
    def r_v(self):
        """Lever arm from optics to tilt-sensing QPD on the vertical plane.
        """
        return self._r_v

    @r_v.setter
    @update_matrices_decorator
    def r_v(self, _r_v):
        """r_v setter
        """
        self._r_v = _r_v

    @property
    def alpha_h(self):
        """Angle of incidence on the horizontal plane.
        """
        return self._alpha_h

    @alpha_h.setter
    @update_matrices_decorator
    def alpha_h(self, _alpha_h):
        """alpha_h setter
        """
        self._alpha_h = _alpha_h

    @property
    def alpha_v(self):
        """Angle of incidence on the vertical plane.
        """
        return self._alpha_v

    @alpha_v.setter
    @update_matrices_decorator
    def alpha_v(self, _alpha_v):
        """alpha_v setter
        """
        self._alpha_v = _alpha_v

    @property
    def r_lens_h(self):
        """Lever arm from optics to the lens on the horizontal plane.
        """
        return self._r_lens_h

    @r_lens_h.setter
    @update_matrices_decorator
    def r_lens_h(self, _r_lens_h):
        """r_lens_h setter
        """
        self._r_lens_h = _r_lens_h

    @property
    def r_lens_v(self):
        """Lever arm from optics to the lens on the vertical plane.
        """
        return self._r_lens_v

    @r_lens_v.setter
    @update_matrices_decorator
    def r_lens_v(self, _r_lens_v):
        """r_lens_v setter
        """
        self._r_lens_v = _r_lens_v

    @property
    def d_h(self):
        """Horizontal distance from the lens to the length-sensing QPD.
        """
        return self._d_h

    @d_h.setter
    @update_matrices_decorator
    def d_h(self, _d_h):
        """d_h setter
        """
        self._d_h = _d_h

    @property
    def d_v(self):
        """Vertical distance from the lens to the length-sensing QPD.
        """
        return self._d_v

    @d_v.setter
    @update_matrices_decorator
    def d_v(self, _d_v):
        """d_v setter
        """
        self._d_v = _d_v

    @property
    def delta_x(self):
        """Horizontal miscentering of the beam spot at the optics plane.
        """
        return self._delta_x

    @delta_x.setter
    @update_matrices_decorator
    def delta_x(self, _delta_x):
        """delta_x setter
        """
        self._delta_x = _delta_x

    @property
    def delta_y(self):
        """Horizontal miscentering of the beam spot at the optics plane.
        """
        return self._delta_y

    @delta_y.setter
    @update_matrices_decorator
    def delta_y(self, _delta_y):
        """delta_y setter
        """
        self._delta_y = _delta_y

    @property
    def phi_tilt(self):
        """Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
        """
        return self._phi_tilt

    @phi_tilt.setter
    @update_matrices_decorator
    def phi_tilt(self, _phi_tilt):
        """phi_tilt setter
        """
        self._phi_tilt = _phi_tilt

    @property
    def phi_len(self):
        """Angle from the length-sensing QPD frame to the yaw-pitch frame.
        """
        return self._phi_len

    @phi_len.setter
    @update_matrices_decorator
    def phi_len(self, _phi_len):
        """phi_len setter
        """
        self._phi_len = _phi_len

    @property
    def f_h(self):
        """Focal length of the convex lens projected on the horizontal plane.
        """
        return self._f_h

    @f_h.setter
    @update_matrices_decorator
    def f_h(self, _f_h):
        """f_h.setter
        """
        self._f_h = _f_h

    @property
    def f_v(self):
        """Focal length of the convex lens projected on the vertical plane.
        """
        return self._f_v

    @f_v.setter
    @update_matrices_decorator
    def f_v(self, _f_v):
        """f_v.setter
        """
        self._f_v = _f_v

    @property
    def format(self):
        """Format of the sensing matrix.

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
        return self._format

    @format.setter
    @update_matrices_decorator
    def format(self, _format):
        """format setter. Format of the sensing matrix.

        Parameters
        ----------
        _format: str
            Choose from
                "OPLEV2EUL"/"OP2EUL": Default sensing matrix from KAGRA MEDM
                    screen with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                    and output (longitudinal, pitch and yaw).
                "xy": Matrix as shown in [1]_.

        References
        ----------
        .. [1]
            Tsang Terrence Tak Lun,
            Sensing Matrices for Optical Levers of the KAGRA Main Optics,
            https://github.com/terrencetec/kagra-optical-lever.
        """
        if _format not in ["OPLEV2EUL", "OL2EUL", "xy"]:
            raise ValueError("Choose from [\"OPLEV2EUL\", \"OL2EUL\", \"xy\"]")
        self._format = _format


class HorizontalOpticalLeverSensingMatrix(OpticalLeverSensingMatrix):
    """Horizontal optical lever sensing matrix.

    Parameters
    ----------
    r: float
        Lever arm.
    alpha_h: float
        Angle of incidence on the horizontal plane.
    r_lens: float, optional
        Lever arm from the optics to the convex lens.
        Default 0.
    f: float, optional
        Focal length of the convex lens.
        Default np.inf.
    alpha_v: float, optional
        Angle of incidence on the vertical plane.
        Default 0.
    phi_tilt: float, optional
        Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
        Default 0.
    phi_len: float, optional
        Angle from the length-sensing QPD frame to the yaw-pitch frame.
        Default 0.
    delta_x: float, optional
        Horizontal miscentering of the beam spot at the optics plane.
        Default 0.
    delta_y: float, optional
        Vertical miscentering of the beam spot at the optics plane.
        Default 0.
    delta_d: float, optional
        Misplacement of the length-sensing QPD.
        Default 0.
    format: str, optional
        Format of the sensing matrix.
        Choose from
            "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                and output (longitudinal, pitch and yaw).
            "xy": Matrix as shown in [1]_.
    coupling_matrix: array, optional
        The coupling matrix.
        Default None.
    *args:
        Variable length arguments passed to OpticalLeverSensingMatrix.
    **kwargs:
        Keyword arguments passed to OpticalLeverSensingMatrix.
    """
    def __new__(cls, r, alpha_h, r_lens=0, f=np.inf,
                alpha_v=0, phi_tilt=0, phi_len=0,
                delta_x=0, delta_y=0, delta_d=0,
                format="OPLEV2EUL", coupling_matrix=None, *args, **kwargs):
        """Constructor

        Parameters
        ----------
        r: float
            Lever arm.
        alpha_h: float
            Angle of incidence on the horizontal plane.
        r_lens: float, optional
            Lever arm from the optics to the convex lens.
            Default 0.
        f: float, optional
            Focal length of the convex lens.
            Default np.inf.
        alpha_v: float, optional
            Angle of incidence on the vertical plane.
            Default 0.
        phi_tilt: float, optional
            Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
            Default 0.
        phi_len: float, optional
            Angle from the length-sensing QPD frame to the yaw-pitch frame.
            Default 0.
        delta_x: float, optional
            Horizontal miscentering of the beam spot at the optics plane.
            Default 0.
        delta_y: float, optional
            Vertical miscentering of the beam spot at the optics plane.
            Default 0.
        delta_d: float, optional
            Misplacement of the length-sensing QPD.
            Default 0.
        format: str, optional
            Format of the sensing matrix.
            Choose from
                "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                    with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                    and output (longitudinal, pitch and yaw).
                "xy": Matrix as shown in [1]_.
        coupling_matrix: array, optional
            The coupling matrix.
            Default None.
        *args:
            Variable length arguments passed to OpticalLeverSensingMatrix.
        **kwargs:
            Keyword arguments passed to OpticalLeverSensingMatrix.
        """
        r_h = r
        r_v = r*np.cos(alpha_h)
        r_lens_h = r_lens
        if f is not np.inf:
            d_h = r_lens*f / (r_lens-f) + delta_d
            f_h = f
            f_v = r*np.cos(alpha_h)
        else:
            d_h = 0
            f_h = np.inf
            f_v = np.inf
        self = super(HorizontalOpticalLeverSensingMatrix, cls).__new__(
            cls,
            r_h=r_h, r_v=r_v, alpha_h=alpha_h, alpha_v=alpha_v,
            r_lens_h=r_lens_h, f_h=f_h, f_v=f_v, d_h=d_h,
            phi_tilt=phi_tilt, phi_len=phi_len,
            delta_x=delta_x, delta_y=delta_y,
            format=format, coupling_matrix=coupling_matrix, *args, **kwargs
        )
        self.r = r
        self.r_lens = r_lens
        self.delta_d = delta_d
        return self

    def __init__(self, *args, **kwargs):
        """Constructor
        """
        pass

    @property
    def r(self):
        """Lever arm.
        """
        return self._r

    @r.setter
    # @OpticalLeverSensingMatrix.update_matrices_decorator
    def r(self, _r):
        """r setter
        """
        self._r = _r
        self.r_h = self.r
        self.r_v = self.r * np.cos(self.alpha_h)

    @property
    def r_lens(self):
        """Lever arm from the optics to the convex lens.
        """
        return self._r_lens

    @r_lens.setter
    def r_lens(self, _r_lens):
        """r_lens setter
        """
        self._r_lens = _r_lens
        self.r_lens_h = self.r_lens

    @property
    def delta_d(self):
        """Misplacement of the length-sensing QPD.
        """
        return self._delta_d

    @delta_d.setter
    def delta_d(self, _delta_d):
        """delta_d setter
        """
        self._delta_d = _delta_d
        self.d_h = self.r_lens*self.f_h/(self.r_lens-self.f_h) + self._delta_d

    @property
    def f(self):
        """Focal length of the convex lens.
        """
        return self._f

    @f.setter
    def f(self, _f):
        """f setter
        """
        self._f = _f
        self.f_h = _f
        self.f_v = _f * np.cos(self.alpha_h)


class VerticalOpticalLeverSensingMatrix(OpticalLeverSensingMatrix):
    """Vertical optical lever sensing matrix.

    Parameters
    ----------
    r: float
        Lever arm.
    alpha_v: float
        Angle of incidence on the vertical plane.
    r_lens: float, optional
        Lever arm from the optics to the convex lens.
        Default 0.
    f: float, optional
        Focal length of the convex lens.
        Default np.inf.
    alpha_h: float, optional
        Angle of incidence on the horizontal plane.
        Default 0.
    phi_tilt: float, optional
        Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
        Default 0.
    phi_len: float, optional
        Angle from the length-sensing QPD frame to the yaw-pitch frame.
        Default 0.
    delta_x: float, optional
        Horizontal miscentering of the beam spot at the optics plane.
        Default 0.
    delta_y: float, optional
        Vertical miscentering of the beam spot at the optics plane.
        Default 0.
    delta_d: float, optional
        Misplacement of the length-sensing QPD.
        Default 0.
    format: str, optional
        Format of the sensing matrix.
        Choose from
            "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                and output (longitudinal, pitch and yaw).
            "xy": Matrix as shown in [1]_.
    coupling_matrix: array, optional
        The coupling matrix.
        Default None.
    *args:
        Variable length arguments passed to OpticalLeverSensingMatrix.
    **kwargs:
        Keyword arguments passed to OpticalLeverSensingMatrix.
    """
    def __new__(cls, r, alpha_v, r_lens=0, f=np.inf,
                alpha_h=0, phi_tilt=0, phi_len=0,
                delta_x=0, delta_y=0, delta_d=0,
                format="OPLEV2EUL", coupling_matrix=None, *args, **kwargs):
        """Constructor

        Parameters
        ----------
        r: float
            Lever arm.
        alpha_v: float
            Angle of incidence on the vertical plane.
        r_lens: float, optional
            Lever arm from the optics to the convex lens.
            Default 0.
        f: float, optional
            Focal length of the convex lens.
            Default np.inf.
        alpha_h: float, optional
            Angle of incidence on the horizontal plane.
            Default 0.
        phi_tilt: float, optional
            Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
            Default 0.
        phi_len: float, optional
            Angle from the length-sensing QPD frame to the yaw-pitch frame.
            Default 0.
        delta_x: float, optional
            Horizontal miscentering of the beam spot at the optics plane.
            Default 0.
        delta_y: float, optional
            Vertical miscentering of the beam spot at the optics plane.
            Default 0.
        delta_d: float, optional
            Misplacement of the length-sensing QPD.
            Default 0.
        format: str, optional
            Format of the sensing matrix.
            Choose from
                "OPLEV2EUL": Default sensing matrix from KAGRA MEDM screen
                    with input (TILT_PIT, TILT_YAW, LEN_PIT, LEN_YAW),
                    and output (longitudinal, pitch and yaw).
                "xy": Matrix as shown in [1]_.
        coupling_matrix: array, optional
            The coupling matrix.
            Default None.
        *args:
            Variable length arguments passed to OpticalLeverSensingMatrix.
        **kwargs:
            Keyword arguments passed to OpticalLeverSensingMatrix.
        """
        r_h = r*np.cos(alpha_v)
        r_v = r
        r_lens_v = r_lens
        if f is not np.inf:
            d_v = r_lens*f / (r_lens-f) + delta_d
            f_h = f*np.cos(alpha_v)
            f_v = f
        else:
            d_v = 0
            f_h = np.inf
            f_v = np.inf
        self = super(VerticalOpticalLeverSensingMatrix, cls).__new__(
            cls,
            r_h=r_h, r_v=r_v, alpha_h=alpha_h, alpha_v=alpha_v,
            r_lens_v=r_lens_v, f_h=f_h, f_v=f_v, d_v=d_v,
            phi_tilt=phi_tilt, phi_len=phi_len,
            delta_x=delta_x, delta_y=delta_y,
            format=format, coupling_matrix=coupling_matrix, *args, **kwargs
        )
        self.r = r
        self.r_lens = r_lens
        self.delta_d = delta_d
        self.f = f
        return self

    def __init__(self, *args, **kwargs):
        """Constructor
        """
        pass

    @property
    def r(self):
        """Lever arm.
        """
        return self._r

    @r.setter
    # @OpticalLeverSensingMatrix.update_matrices_decorator
    def r(self, _r):
        """r setter
        """
        self._r = _r
        self.r_h = self.r * np.cos(self.alpha_v)
        self.r_v = self.r

    @property
    def r_lens(self):
        """Lever arm from the optics to the convex lens.
        """
        return self._r_lens

    @r_lens.setter
    def r_lens(self, _r_lens):
        """r_lens setter
        """
        self._r_lens = _r_lens
        self.r_lens_v = self.r_lens

    @property
    def delta_d(self):
        """Misplacement of the length-sensing QPD.
        """
        return self._delta_d

    @delta_d.setter
    def delta_d(self, _delta_d):
        """delta_d setter
        """
        self._delta_d = _delta_d
        self.d_v = self.r_lens*self.f_v/(self.r_lens-self.f_v) + self._delta_d

    @property
    def f(self):
        """Focal length of the convex lens.
        """
        return self._f

    @f.setter
    def f(self, _f):
        """f setter
        """
        self._f = _f
        self.f_h = _f * np.cos(self.alpha_v)
        self.f_v = _f


def c_align(r_h, r_v, alpha_h, alpha_v,
            r_lens_h=0, r_lens_v=0, d_h=0, d_v=0,
            f_h=np.inf, f_v=np.inf,
            roundoff=6):
    r"""Return optical lever sensing matrix for a perfectly aligned case.

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
    f_h : float, optional,
        Focal length of the lens projected to the horizontal plane.
        Defaults ``np.inf`` (no lens).
    f_v : float, optional,
        Focal length of the lens projected to the vertical plane.
        Defaults ``np.inf`` (no lens).
    roundoff: int, optional
        How many decimal places to keep.

    Returns
    -------
    array
        The aligned optical lever sensing matrix

    Notes
    -----
    See :math:`\mathbf{C}_\mathrm{align}` from [1]_.

    If `f_h` or `f_v` or (`d_h` and `d_v`) or (`r_lens_h` and `r_lens_v`)
    are not  specified, then we assume no length-sensing QPD so first column,
    third row, and forth row will be 0.
    elif `f_h` and `f_v` is specified, (`d_h` or `r_lens_h`) are not specified,
    then third row will be 0.
    elif `f_h` and `f_v` is specified, (`d_v` or `r_lens_v`) are not specified,
    then forth row will be 0.

    References
    ----------
    .. [1]
        Tsang Terrence Tak Lun,
        Sensing Matrices for Optical Levers of the KAGRA Main Optics,
        https://github.com/terrencetec/kagra-optical-lever.
    """
    # print(r_h, r_v, alpha_h, alpha_v, r_lens_h, r_lens_v, d_h, d_v, f)
    c_align_inv = np.array([
            [2*np.sin(alpha_h), 0, 2*r_h],
            [2*np.sin(alpha_v), 2*r_v, 0],
            [2*np.sin(alpha_h)*(1-d_h/f_h), 0, 2*((1-d_h/f_h)*r_lens_h + d_h)],
            [2*np.sin(alpha_v)*(1-d_v/f_v), 2*((1-d_v/f_v)*r_lens_v + d_v), 0]
        ])
    if (f_h == np.inf or f_v == np.inf
       or (d_h == 0 and d_v == 0) or (r_lens_h == 0 and r_lens_v == 0)):
        # If the length-sensing optical lever doesn't exist.
        c_align_inv[2:] = np.zeros_like(c_align_inv[2:])
        c_align_inv[:, 0] = np.zeros_like(c_align_inv[:, 0])
    elif d_h == 0 or r_lens_h == 0:
        # For vertical optical lever setup.
        c_align_inv[2, :] = np.zeros_like(c_align_inv[2, :])
    elif d_v == 0 or r_lens_v == 0:
        # For horizontal optical lever setup.
        c_align_inv[3, :] = np.zeros_like(c_align_inv[3, :])

    return np.linalg.pinv(c_align_inv).round(roundoff)


def c_rotation(phi_tilt, phi_len):
    r"""Returns the rotation transformation matrix for tilt and length QPDs.

    Parameters
    ----------
    phi_tilt: float
        Angle from the tilt-sensing QPD frame to the yaw-pitch frame.
    phi_len: float
        Angle from the length-sensing QPD frame to the yaw-pitch frame.

    Returns
    -------
    array
        Matrix that transform the QPD frames to the yaw-pitch frame.

    Notes
    -----
    See :math:`\mathbf{C}_\mathrm{rotation}` from [1]_

    References
    ----------
    .. [1]
        Tsang Terrence Tak Lun,
        Sensing Matrices for Optical Levers of the KAGRA Main Optics,
        https://github.com/terrencetec/kagra-optical-lever.
    """
    _c_rotation = np.array([
            [np.cos(phi_tilt), np.sin(phi_tilt), 0, 0],
            [-np.sin(phi_tilt), np.cos(phi_tilt), 0, 0],
            [0, 0, np.cos(phi_len), np.sin(phi_len)],
            [0, 0, -np.sin(phi_len), np.cos(phi_len)]
        ])
    return _c_rotation


def c_miscenter(delta_x, delta_y):
    """Returns the matrix for correcting miscentered optical lever beam.

    Parameters
    ----------
    delta_x: float
        Horizontal miscentering of the beam spot at the optics plane.
    delta_y: float
        Vertical miscentering of the beam spot at the optics plane.

    Returns
    -------
    array
        The miscentering correction matrix.
    """
    c_miscenter_inv = np.array([
            [1, delta_y, delta_x],
            [0, 1, 0],
            [0, 0, 1]
        ])
    return np.linalg.inv(c_miscenter_inv)
