header = """layout="dot";
            concentrate="true";
            rankdir="LR";
            orderoutput="edgesfirst";
            splines="compound";
            nodesep="1"; ranksep="1";
        """ # imagepath="K:\Clients\AFL - AFL\2021\015 - Oakridge AB - OKRG\OKRG 1031B\DFD";

node_label = """<<table border='0' cellspacing='0'>
                    <tr><td port='sheet'    border='0' bgcolor='white'>{Sheet}</td></tr>
                    <tr><td port='splice'   border='0'><b>{Splice}}</b></td></tr>
                    <tr><td port='struc'    border='0'>{Struc}</td></tr>
                    <tr><td port='fcp'      border='0'>{FCP}</td></tr>
                    <tr><td port='stype'    border='0'><b>{SType}</b></td></tr>
                    <tr><td port='sss'      border='0' bgcolor='#FFC000'>{SSS}</td></tr>
                    <tr><td port='fibre'    border='0' bgcolor='#FFCCFF'>{LiveCount}</td></tr>
                    <tr><td port='spare'    border='0' bgcolor='#FFFF00'>{Spare0}</td></tr>
                    <tr><td port='rsvd'     border='0' bgcolor='#E26B0A'>{RSVD1}</td></tr>
                    <tr><td port='spare2'     border='0' bgcolor='#FFFF00'>{Spare1}</td></tr>
                    <tr><td port='rsvd2'     border='0' bgcolor='#E26B0A'>{RSVD2}</td></tr>
                    <tr><td port='spare3'     border='0' bgcolor='#FFFF00'>{Spare2}</td></tr>
                   <tr><td port='spl_ac'    border='0' bgcolor='white'>"{SpliceActivity}</td></tr>
        </table>>"""

edge_label = "{CableActivity}\n{Capacity}\n{FibreAllocation}\n{DeadRange}"

node = 'node[ colorscheme="X11" shape="record" fillcolor="Green" fontname="Calibri" fontsize="30" style="filled" ];'
edge = 'edge[ colorscheme="X11" color="Gray24" penwidth="2" arrowsize="0" fontname="Calibri" fontsize="30" ];'