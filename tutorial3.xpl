<plask loglevel="important">

<defines>

  <define name="mesa" value="32"/>
  <define name="aperture_radius" value="8."/>
  <define name="n_contact_pos" value="8."/>
  <define name="aperture_thickness" value="8."/>
  <define name="DBR1_thickness" value="8."/>
  <define name="DBR2_thickness" value="8."/>
  <define name="QW_ne" value="8."/>
  <define name="L_boundry_T" value="8."/>
  <define name="L_boundry_V" value="8."/>
  <define name="n_top_dbr" value="8."/>
  <define name="n_bottom_dbr" value="8."/>
</defines>

<materials>
  <material name="InGaAsQW" base="In(0.22)GaAs">
    <nr>QW_ne</nr>
    <absp>0</absp>
    <A>110000000</A>
    <B>7e-011-1.08e-12*(T-300)</B>
    <C>1e-029+1.4764e-33*(T-300)</C>
    <D>10+0.01667*(T-300)</D>
  </material>
</materials>

<geometry>
  <cylindrical2d name="GeoE" axes="r,z">
    <stack>
      <item right="{n_contact_pos}">
        <rectangle name="n-contact" material="Au" dr="4" dz="0.0500"/>
      </item>
      <stack name="VCSEL">
        <rectangle material="GaAs:Si=2e+18" dr="{mesa/2}" dz="0.0700"/>
        <stack name="top-DBR" repeat="{n_top_dbr}">
          <rectangle material="Al(0.73)GaAs:Si=2e+18" dr="{mesa/2}" dz="{DBR1_thickness}"/>
          <rectangle material="GaAs:Si=2e+18" dr="{mesa/2}" dz="{DBR2_thickness}"/>
        </stack>
        <shelf>
          <rectangle name="aperture" material="AlAs:Si=2e+18" dr="{aperture_radius/2}" dz="{aperture_thickness}"/>
          <rectangle name="oxide" material="AlOx" dr="{(mesa-aperture_radius)/2}" dz="0.0160"/>
        </shelf>
        <rectangle material="Al(0.73)GaAs:Si=2e+18" dr="{mesa/2}" dz="0.0635"/>
        <rectangle material="GaAs:Si=5e+17" dr="{mesa/2}" dz="0.1160"/>
        <stack name="junction" role="active">
          <stack repeat="4">
            <rectangle name="QW" role="QW" material="InGaAsQW" dr="{mesa/2}" dz="0.0050"/>
            <rectangle material="GaAs" dr="{mesa/2}" dz="0.0050"/>
          </stack>
          <again ref="QW"/>
        </stack>
        <rectangle material="GaAs:C=5e+17" dr="{mesa/2}" dz="0.1160"/>
        <stack name="bottom-DBR" repeat="{n_bottom_dbr}">
          <rectangle material="Al(0.73)GaAs:C=2e+18" dr="{mesa/2}" dz="{DBR1_thickness}"/>
          <rectangle material="GaAs:C=2e+18" dr="{mesa/2}" dz="{DBR2_thickness}"/>
        </stack>
      </stack>
      <zero/>
      <rectangle name="p-contact" material="GaAs:C=2e+18" dr="{mesa/2}" dz="5."/>
    </stack>
  </cylindrical2d>
  <cylindrical2d name="GeoT" axes="r,z">
    <stack>
      <item right="{mesa/2-1}">
        <rectangle material="Au" dr="4" dz="0.0500"/>
      </item>
      <again ref="VCSEL"/>
      <zero/>
      <rectangle material="GaAs:C=2e+18" dr="2500." dz="150."/>
      <rectangle material="Cu" dr="2500." dz="5000."/>
    </stack>
  </cylindrical2d>
  <cylindrical2d name="GeoO" axes="r,z" outer="extend" bottom="GaAs" top="air">
    <again ref="VCSEL"/>
  </cylindrical2d>
</geometry>

<grids>
  <generator method="divide" name="default" type="rectangular2d">
    <postdiv by0="3" by1="2"/>
    <refinements>
      <axis0 object="oxide" at="-0.1"/>
      <axis0 object="oxide" at="-0.05"/>
      <axis0 object="aperture" at="0.1"/>
    </refinements>
  </generator>
  <generator method="divide" name="optical" type="ordered">
    <prediv by="10"/>
  </generator>
</grids>

<solvers>
  <meta name="SOLVER" solver="ThresholdSearchCyl" lib="shockley">
    <geometry electrical="GeoE" optical="GeoO" thermal="GeoT"/>
    <mesh electrical="default" optical="optical" thermal="default"/>
    <optical dlam="0.01" lam0="977." maxlam="980." vat="0"/>
    <root bcond="0" vmax="1.6" vmin="1.4"/>
    <voltage>
      <condition value="{L_boundry_V}">
        <place side="bottom" object="p-contact"/>
      </condition>
      <condition value="0.0">
        <place side="top" object="n-contact"/>
      </condition>
    </voltage>
    <temperature>
      <condition place="bottom" value="{L_boundry_T}"/>
    </temperature>
    <junction beta0="11" js0="1"/>
    <diffusion accuracy="0.005" fem-method="parabolic"/>
    <gain lifetime="0.5" matrix-elem="10"/>
    <optical-root determinant="full"/>
  </meta>
</solvers>

</plask>
