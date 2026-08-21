%% =======================================================================
%  ECOLI - Construccion de las etapas del dataset
%  E0 crudo -> E1 outliers -> E2 balanceo -> E3 estandarizado
%           -> E4 normalizado -> E5 seleccion de variables
%  Cada etapa se guarda en CSV para poder abrirla en Classification Learner.
% =======================================================================
clear; clc; close all;
rng(42);                                   % para que el SMOTE sea repetible

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'ecoli', 'figuras');
dir_et  = fullfile(base, 'resultados', 'ecoli', 'etapas');
xls     = fullfile(base, 'Resultados_Ecoli.xlsx');
load(fullfile(base, 'resultados', 'ecoli', 'ecoli_crudo.mat'));

E = struct();   % aca se van guardando las etapas

%% --- E0: crudo ---------------------------------------------------------
E(1).nombre = 'E0_crudo';
E(1).desc   = 'Dataset tal como viene de UCI, 8 clases, 7 predictoras';
E(1).X = T{:, vars};
E(1).y = y;
E(1).vars = vars;

%% --- E1: correccion de outliers y variables inutiles -------------------
% Dos decisiones:
%  a) se quita chg. El 99.7% de las filas tiene el mismo valor, o sea que
%     no aporta varianza y el chi2 que salio significativo lo produce
%     una sola muestra. Con eso no se generaliza nada.
%  b) los atipicos se WINSORIZAN (se recortan al limite 1.5*IQR) en vez de
%     borrarse: son 22 valores en 2 variables sobre 336 muestras y con una
%     muestra tan chica borrar filas cuesta caro.
vars1 = setdiff(vars, {'chg'}, 'stable');
X1    = T{:, vars1};
cols_cont = find(ismember(vars1, contin));       % la regla IQR solo a las continuas
[X1, info_out] = tratar_outliers(X1, cols_cont, 'winsor', 1.5);

E(2).nombre = 'E1_outliers';
E(2).desc   = 'Sin chg (varianza nula) + winsorizacion 1.5*IQR en continuas';
E(2).X = X1;  E(2).y = y;  E(2).vars = vars1;

fprintf('E1: se winsorizaron valores en %d variables; filas tocadas: %d (%.1f%%)\n', ...
        sum(info_out.detalle(:,1) > 0), sum(info_out.filas_malas), info_out.pct_filas);

%% --- E2: balanceo de clases -------------------------------------------
% Antes de balancear hay que sacar las clases con muy pocas muestras:
% imL(2), imS(2) y omL(5). Con n<10 no se puede ni validar de forma cruzada
% ni generar sinteticos decentes (SMOTE necesita al menos k vecinos).
% Son 9 muestras de 336, o sea 2.7% del dataset.
[cnt, nom] = groupcounts(y);
clases_ok  = nom(cnt >= 10);
mask       = ismember(y, clases_ok);
fprintf('E2: se descartan las clases %s (%d muestras, %.1f%%)\n', ...
        strjoin(nom(cnt < 10)', ', '), sum(~mask), 100*sum(~mask)/numel(y));

% SMOTE y no submuestreo: con 327 muestras, recortar cp de 143 a 20
% dejaria 100 muestras en total y no alcanzaria para entrenar nada.
[X2, y2] = balancear(X1(mask, :), y(mask), 'smote');

E(3).nombre = 'E2_balanceado';
E(3).desc   = 'E1 + clases con n<10 fuera + SMOTE hasta igualar la mayoritaria';
E(3).X = X2;  E(3).y = y2;  E(3).vars = vars1;

%% --- E3: estandarizacion (z-score) ------------------------------------
E(4).nombre = 'E3_estandarizado';
E(4).desc   = 'E2 con cada variable centrada en 0 y desviacion 1';
E(4).X = zscore(X2);  E(4).y = y2;  E(4).vars = vars1;

%% --- E4: normalizacion (min-max a [0,1]) ------------------------------
mn = min(X2);  mx = max(X2);  rg = mx - mn;  rg(rg == 0) = 1;
E(5).nombre = 'E4_normalizado';
E(5).desc   = 'E2 reescalado al rango [0,1]';
E(5).X = (X2 - mn) ./ rg;  E(5).y = y2;  E(5).vars = vars1;

%% --- E5: seleccion de variables ---------------------------------------
% alm1 y alm2 tienen Pearson 0.81 y son las dos con VIF mas alto (4.05 y
% 3.71). Se deja alm1, que es la de mayor F en el ANOVA, y se quita alm2.
vars5 = setdiff(vars1, {'alm2'}, 'stable');
sel   = ismember(vars1, vars5);
E(6).nombre = 'E5_seleccion';
E(6).desc   = 'E3 sin alm2 (correlacion 0.81 con alm1)';
E(6).X = E(4).X(:, sel);  E(6).y = y2;  E(6).vars = vars5;

%% --- Resumen de etapas + exportar CSV ---------------------------------
filas = {};
for i = 1:numel(E)
    Xi = E(i).X;  yi = E(i).y;
    [ci, ni] = groupcounts(yi);
    IR  = max(ci)/min(ci);
    Hn  = -sum((ci/numel(yi)).*log(ci/numel(yi))) / log(numel(ni));
    filas(end+1, :) = {E(i).nombre, E(i).desc, size(Xi,1), size(Xi,2), numel(ni), ...
                       IR, Hn, min(Xi(:)), max(Xi(:)), mean(Xi(:)), std(Xi(:))}; %#ok<SAGROW>

    % CSV listo para arrastrar a Classification Learner
    Ti = array2table(Xi, 'VariableNames', E(i).vars);
    Ti.clase = yi;
    writetable(Ti, fullfile(dir_et, ['ecoli_' E(i).nombre '.csv']));
end
Etapas = cell2table(filas, 'VariableNames', ...
    {'Etapa','Descripcion','N_filas','N_vars','N_clases','IR','Entropia_norm', ...
     'Min_global','Max_global','Media_global','Desv_global'});
disp(Etapas);

%% --- Graficos de control por etapa ------------------------------------
for i = 1:numel(E)
    f = figure('Visible','off','Position',[100 100 1250 450]);

    subplot(1,3,1);
    boxplot(E(i).X, 'Labels', E(i).vars);
    title('Boxplot de las predictoras'); ylabel('valor');

    subplot(1,3,2);
    histogram(E(i).X(:), 40, 'FaceColor',[0.2 0.5 0.8]);
    title('Histograma de todos los valores'); xlabel('valor'); ylabel('frec');

    subplot(1,3,3);
    [ci, ni] = groupcounts(E(i).y);
    bar(categorical(ni, ni), ci, 'FaceColor',[0.85 0.4 0.3]);
    title(sprintf('Balance de clase (IR = %.1f)', max(ci)/min(ci)));
    ylabel('muestras');

    sgtitle(sprintf('Ecoli - %s : %s', strrep(E(i).nombre,'_',' '), E(i).desc), ...
            'FontSize', 10);
    guardar_fig(f, dir_fig, sprintf('10_etapa_%s', E(i).nombre));
end

% comparacion del balance antes y despues, en una sola figura
f = figure('Visible','off','Position',[100 100 1000 420]);
subplot(1,2,1);
[c0, n0] = groupcounts(E(1).y);  bar(categorical(n0,n0), c0, 'FaceColor',[0.85 0.4 0.3]);
title(sprintf('Antes: 8 clases, IR = %.1f', max(c0)/min(c0))); ylabel('muestras');
subplot(1,2,2);
[c2, n2] = groupcounts(E(3).y);  bar(categorical(n2,n2), c2, 'FaceColor',[0.35 0.65 0.4]);
title(sprintf('Despues: %d clases, IR = %.1f', numel(n2), max(c2)/min(c2)));
sgtitle('Ecoli - efecto del balanceo sobre la variable objetivo');
guardar_fig(f, dir_fig, '11_balance_antes_despues');

%% --- Exportar ---------------------------------------------------------
writetable(Etapas, xls, 'Sheet', 'E3_Etapas');
save(fullfile(base,'resultados','ecoli','ecoli_etapas.mat'), 'E', 'vars1', 'contin');
fprintf('\nPaso 3 (etapas) terminado. CSV en resultados/ecoli/etapas\n');
