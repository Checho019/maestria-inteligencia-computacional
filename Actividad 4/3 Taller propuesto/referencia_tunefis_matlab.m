% Ejemplo Tune FIS de MathWorks con las cifras que el cuaderno usa como referencia.
% Imprime el sistema inicial de genfis, el RMSE de cada época de ANFIS y los
% parámetros finales, para compararlos con el ANFIS programado en Python.
x = (0:0.1:10)';
y = sin(2*x)./exp(x/5);
opciones = genfisOptions("GridPartition");
opciones.NumMembershipFunctions = 5;
fisin = genfis(x, y, opciones);

for k = 1:numel(fisin.Inputs.MembershipFunctions)
    m = fisin.Inputs.MembershipFunctions(k);
    fprintf("campana inicial %d  %s [%s]\n", k, m.Type, num2str(m.Parameters, "%.6f "));
end
fprintf("RMSE inicial %.7f\n", sqrt(mean((evalfis(fisin, x) - y).^2)));

[entrada, salida, ~] = getTunableSettings(fisin);
fisout = tunefis(fisin, [entrada; salida], x, y, tunefisOptions(Method="anfis"));

fprintf("RMSE final %.7f\n", sqrt(mean((evalfis(fisout, x) - y).^2)));
for k = 1:numel(fisout.Inputs.MembershipFunctions)
    m = fisout.Inputs.MembershipFunctions(k);
    fprintf("campana final %d  [%s]\n", k, num2str(m.Parameters, "%.6f "));
end
for k = 1:numel(fisout.Outputs.MembershipFunctions)
    m = fisout.Outputs.MembershipFunctions(k);
    fprintf("consecuente final %d  [%s]\n", k, num2str(m.Parameters, "%.6f "));
end

% Segunda parte. 300 épocas con datos de comprobación en los puntos intermedios,
% con anfis para obtener las curvas de error y el tamaño de paso de cada época.
xv = (0.05:0.1:9.95)';
yv = sin(2*xv)./exp(xv/5);
opc = anfisOptions(InitialFIS=fisin, EpochNumber=300, ValidationData=[xv yv], ...
    DisplayANFISInformation=false, DisplayErrorValues=false, DisplayStepSize=false, DisplayFinalResults=false);
[~, errEnt, paso, ~, errVal] = anfis([x y], opc);
[valMin, epMin] = min(errVal);
fprintf("300 épocas. RMSE de entrenamiento en la época 10 %.5f y en la 300 %.5f\n", errEnt(10), errEnt(end));
fprintf("300 épocas. RMSE de comprobación mínimo %.5f en la época %d\n", valMin, epMin);
fprintf("300 épocas. Paso final %.4f\n", paso(end));
fprintf("Épocas en que cambia el paso:");
fprintf(" %d", find(diff(paso) ~= 0) + 1);
fprintf("\n");
