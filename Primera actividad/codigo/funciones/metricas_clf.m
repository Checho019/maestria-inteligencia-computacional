function m = metricas_clf(yreal, ypred, clases, clase_pos)
% Metricas de clasificacion a partir de la matriz de confusion.
% Se reportan varias a proposito: con clases desbalanceadas la exactitud
% sola enganya (ver discusion en el informe).

C = confusionmat(cellstr(yreal), cellstr(ypred), 'Order', clases);
n = sum(C(:));

aciertos  = diag(C);
por_fila  = sum(C, 2);      % soporte real de cada clase
por_col   = sum(C, 1)';     % veces que se predijo cada clase

recall    = aciertos ./ max(por_fila, 1);
precision = aciertos ./ max(por_col, 1);
f1        = 2*precision.*recall ./ max(precision + recall, eps);
f1(por_fila == 0) = NaN;

m.exactitud     = sum(aciertos) / n;
m.exact_balance = mean(recall(por_fila > 0));      % promedio de recalls
m.f1_macro      = mean(f1(~isnan(f1)));

% kappa de Cohen: corrige la exactitud por el acierto esperado al azar
pe = sum(por_fila .* por_col) / n^2;
m.kappa = (m.exactitud - pe) / max(1 - pe, eps);

% si es binario, se reportan tambien las metricas de la clase positiva
m.recall_pos = NaN; m.precision_pos = NaN; m.f1_pos = NaN;
if nargin > 3 && ~isempty(clase_pos)
    ip = find(strcmp(clases, clase_pos), 1);
    if ~isempty(ip)
        m.recall_pos    = recall(ip);
        m.precision_pos = precision(ip);
        m.f1_pos        = f1(ip);
    end
end
m.confusion = C;
end
