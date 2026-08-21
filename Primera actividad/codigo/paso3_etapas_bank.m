%% =======================================================================
%  BANK MARKETING - Construccion de las etapas del dataset
%  B0 crudo -> B1 correcciones/outliers -> B2 balanceo -> B3 estandarizado
%           -> B4 normalizado -> B5 seleccion de variables
%
%  Todas las etapas quedan en matriz numerica: las categoricas se pasan a
%  variables indicadoras (one-hot). Se hace asi porque KNN, LDA y la
%  regresion logistica necesitan numeros, y ademas es lo que Classification
%  Learner termina haciendo por dentro con esos modelos.
% =======================================================================
clear; clc; close all;
rng(42);

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'bank', 'figuras');
dir_et  = fullfile(base, 'resultados', 'bank', 'etapas');
xls     = fullfile(base, 'Resultados_Bank.xlsx');
load(fullfile(base, 'resultados', 'bank', 'bank_crudo.mat'));

E = struct();

%% --- B0: crudo ---------------------------------------------------------
% Tal como viene: incluye duration y deja pdays con el -1.
[X0, v0] = codificar(T, num, cat);
E(1).nombre = 'B0_crudo';
E(1).desc   = 'Dataset completo con one-hot, incluye duration y pdays=-1';
E(1).X = X0;  E(1).y = y;  E(1).vars = v0;
fprintf('B0: %d filas x %d columnas tras el one-hot\n', size(X0,1), size(X0,2));

%% --- B1: correcciones + outliers --------------------------------------
% Tres decisiones, en orden de importancia:
%
% a) Se saca duration. La documentacion de UCI lo dice explicito: la duracion
%    de la llamada solo se conoce DESPUES de hacerla, y si la llamada dura 0
%    segundos la respuesta es "no" por definicion. Usarla es hacer trampa:
%    el modelo predice con informacion del futuro. Es la variable con mayor
%    efecto de todas (d de Cohen = 1.34) justamente por eso.
%
% b) pdays = -1 no es un numero, es una etiqueta que significa "nunca lo
%    habian contactado" (81.7% de los registros). Si se deja como numero, el
%    modelo interpreta que estos clientes fueron contactados hace -1 dias.
%    Se parte en dos: una bandera binaria y el valor real solo cuando aplica.
%
% c) Los atipicos se winsorizan con 1.5*IQR, pero solo en las variables donde
%    el IQR es distinto de cero (age, balance, duration, campaign). En pdays
%    y previous mas del 75% de los datos vale lo mismo, el IQR da 0 y la regla
%    de Tukey las volveria constantes. A esas se les recorta el percentil 99.
T1 = T;
T1.contactado_antes = double(T1.pdays >= 0);
T1.pdays(T1.pdays < 0) = 0;
num1 = {'age','balance','day','campaign','pdays','previous','contactado_antes'};
cat1 = cat;

[X1, v1] = codificar(T1, num1, cat1);

% winsorizacion 1.5*IQR en las que tienen IQR > 0
cols_iqr = find(ismember(v1, {'age','balance','campaign'}));
[X1, info_out] = tratar_outliers(X1, cols_iqr, 'winsor', 1.5);
fprintf('B1: winsorizadas %s -> %d filas tocadas (%.1f%%)\n', ...
        strjoin(v1(cols_iqr), ', '), sum(info_out.filas_malas), info_out.pct_filas);

% recorte al percentil 99 para las de IQR = 0
for nombre = {'pdays','previous'}
    jj = strcmp(v1, nombre{1});
    tope = quantile(X1(:, jj), 0.99);
    n_rec = sum(X1(:, jj) > tope);
    X1(X1(:, jj) > tope, jj) = tope;
    fprintf('B1: %s recortada en el percentil 99 (%.0f), %d valores tocados\n', ...
            nombre{1}, tope, n_rec);
end

E(2).nombre = 'B1_correcciones';
E(2).desc   = 'Sin duration + pdays convertido en bandera + winsorizacion';
E(2).X = X1;  E(2).y = y;  E(2).vars = v1;

%% --- B2: balanceo de clases -------------------------------------------
% Aca se submuestrea y NO se hace SMOTE, al reves que en Ecoli. La razon es
% el tamano: hay 5289 "yes", asi que recortando los "no" quedan 10578
% registros, suficientes para entrenar. Sobremuestrear hubiera dejado 79844
% filas, con 34633 sinteticas inventadas, y ademas volveria lentisimo el
% Classification Learner.
[X2, y2] = balancear(X1, y, 'submuestreo');
E(3).nombre = 'B2_balanceado';
E(3).desc   = 'B1 con submuestreo aleatorio de la clase no hasta 50/50';
E(3).X = X2;  E(3).y = y2;  E(3).vars = v1;
fprintf('B2: %d filas (%d por clase)\n', size(X2,1), size(X2,1)/2);

%% --- B3: estandarizacion ----------------------------------------------
E(4).nombre = 'B3_estandarizado';
E(4).desc   = 'B2 con z-score en todas las columnas';
E(4).X = zscore(X2);  E(4).y = y2;  E(4).vars = v1;

%% --- B4: normalizacion ------------------------------------------------
mn = min(X2); mx = max(X2); rg = mx - mn; rg(rg == 0) = 1;
E(5).nombre = 'B4_normalizado';
E(5).desc   = 'B2 reescalado al rango [0,1]';
E(5).X = (X2 - mn) ./ rg;  E(5).y = y2;  E(5).vars = v1;

%% --- B5: seleccion de variables ---------------------------------------
% Se queda con las columnas mejor rankeadas por MRMR sobre el propio B2.
% Se toman las 20 primeras, que es mas o menos la mitad.
n_sel = 20;
[idx_sel, ~] = fscmrmr(X2, y2);
sel = sort(idx_sel(1:n_sel));
E(6).nombre = 'B5_seleccion';
E(6).desc   = sprintf('B3 con las %d columnas mejor rankeadas por MRMR', n_sel);
E(6).X = E(4).X(:, sel);  E(6).y = y2;  E(6).vars = v1(sel);
fprintf('B5: se conservan %d de %d columnas\n', n_sel, numel(v1));

%% --- Resumen + exportar CSV -------------------------------------------
filas = {};
for i = 1:numel(E)
    Xi = E(i).X;  yi = E(i).y;
    n_si = sum(strcmp(yi, 'yes'));  n_no = sum(strcmp(yi, 'no'));
    filas(end+1,:) = {E(i).nombre, E(i).desc, size(Xi,1), size(Xi,2), ...
                      n_no, n_si, n_no/n_si, max(n_no,n_si)/numel(yi), ...
                      min(Xi(:)), max(Xi(:))};   %#ok<SAGROW>

    Ti = array2table(Xi, 'VariableNames', E(i).vars);
    Ti.clase = yi;
    writetable(Ti, fullfile(dir_et, ['bank_' E(i).nombre '.csv']));
end
Etapas = cell2table(filas, 'VariableNames', ...
    {'Etapa','Descripcion','N_filas','N_columnas','N_no','N_yes','IR', ...
     'Tasa_base','Min_global','Max_global'});
disp(Etapas);

%% --- Graficos por etapa (solo las columnas originalmente numericas) ---
for i = 1:numel(E)
    cols_n = find(ismember(E(i).vars, [num num1]));
    f = figure('Visible','off','Position',[100 100 1300 470]);

    subplot(1,3,1);
    Z = normalize(E(i).X(:, cols_n), 'range');   % escala comun solo para verlos juntos
    boxplot(Z, 'Labels', E(i).vars(cols_n));
    set(gca,'XTickLabelRotation',45,'FontSize',8);
    title('Numericas (reescaladas solo para dibujarlas juntas)');

    subplot(1,3,2);
    histogram(E(i).X(:, strcmp(E(i).vars,'age')), 40, 'FaceColor',[0.2 0.5 0.8]);
    title('Histograma de age'); xlabel('valor'); ylabel('frec');

    subplot(1,3,3);
    n_no = sum(strcmp(E(i).y,'no'));  n_si = sum(strcmp(E(i).y,'yes'));
    bar(categorical({'no','yes'}), [n_no n_si], 'FaceColor',[0.85 0.4 0.3]);
    title(sprintf('Balance (IR = %.2f)', n_no/n_si)); ylabel('registros');

    sgtitle(sprintf('Bank - %s : %s', strrep(E(i).nombre,'_',' '), E(i).desc), 'FontSize', 10);
    guardar_fig(f, dir_fig, sprintf('10_etapa_%s', E(i).nombre));
end

f = figure('Visible','off','Position',[100 100 1000 420]);
subplot(1,2,1);
bar(categorical({'no','yes'}), [sum(strcmp(y,'no')) sum(strcmp(y,'yes'))], 'FaceColor',[0.85 0.4 0.3]);
title(sprintf('Antes: IR = %.2f', sum(strcmp(y,'no'))/sum(strcmp(y,'yes')))); ylabel('registros');
subplot(1,2,2);
bar(categorical({'no','yes'}), [sum(strcmp(y2,'no')) sum(strcmp(y2,'yes'))], 'FaceColor',[0.35 0.65 0.4]);
title('Despues: IR = 1.00');
sgtitle('Bank - efecto del submuestreo sobre la variable objetivo');
guardar_fig(f, dir_fig, '11_balance_antes_despues');

%% --- Exportar ---------------------------------------------------------
writetable(Etapas, xls, 'Sheet', 'B3_Etapas');
save(fullfile(base,'resultados','bank','bank_etapas.mat'), 'E', 'num1', 'cat1');
fprintf('\nPaso 3 (etapas bank) terminado. CSV en resultados/bank/etapas\n');


function [X, nombres] = codificar(T, num, cat)
% Pasa la tabla a matriz numerica. Las categoricas se convierten en columnas
% 0/1, una por nivel menos el primero (se deja fuera para no crear columnas
% linealmente dependientes entre si).
X = T{:, num};
nombres = num;
for j = 1:numel(cat)
    v = categorical(T.(cat{j}));
    niveles = categories(v);
    D = dummyvar(v);
    X = [X, D(:, 2:end)];                                       %#ok<AGROW>
    for k = 2:numel(niveles)
        nombres{end+1} = matlab.lang.makeValidName([cat{j} '_' niveles{k}]);  %#ok<AGROW>
    end
end
end
