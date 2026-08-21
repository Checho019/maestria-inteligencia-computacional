%% =======================================================================
%  ECOLI - Modelos en cada etapa del dataset
%  Se entrena lo mismo (5 clasificadores, validacion cruzada 5-fold) sobre
%  cada version del dataset para ver que aporta cada correccion.
%
%  Se reportan DOS validaciones a proposito:
%   (a) directa  -> se le pasa al modelo el CSV ya transformado, que es
%                   exactamente lo que hace Classification Learner.
%   (b) honesta  -> el balanceo y el escalado se calculan solo con el bloque
%                   de entrenamiento de cada fold.
%  La diferencia entre las dos es el resultado mas importante del trabajo.
% =======================================================================
clear; clc; close all;
rng(42);

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'ecoli', 'figuras');
xls     = fullfile(base, 'Resultados_Ecoli.xlsx');
load(fullfile(base, 'resultados', 'ecoli', 'ecoli_etapas.mat'));
load(fullfile(base, 'resultados', 'ecoli', 'ecoli_crudo.mat'), 'T', 'y', 'vars');

modelos = {'Arbol','KNN','LDA','NaiveBayes','SVM'};

%% --- (a) Validacion directa sobre cada etapa ---------------------------
Res = table();
for i = 1:numel(E)
    fprintf('--- %s ---\n', E(i).nombre);
    op = struct('k',5, 'semilla',42, 'modelos',{modelos});
    Ti = evaluar_cv(E(i).X, E(i).y, op);
    Ti.Etapa = repmat({E(i).nombre}, height(Ti), 1);
    Ti.N     = repmat(size(E(i).X,1), height(Ti), 1);
    Ti.Clases= repmat(numel(unique(E(i).y)), height(Ti), 1);
    Res = [Res; Ti];   %#ok<AGROW>
end
Res = movevars(Res, {'Etapa','N','Clases'}, 'Before', 'Modelo');
Res = removevars(Res, {'Recall_pos','Precision_pos','F1_pos'});   % solo aplican a binario
disp(Res);

%% --- (b) Validacion honesta -------------------------------------------
% Partimos de E1 con las clases raras ya fuera, PERO sin balancear ni
% escalar. El balanceo/escalado se hace dentro de cada fold.
[cnt, nom] = groupcounts(y);
clases_ok = nom(cnt >= 10);
mask = ismember(y, clases_ok);
Xh = E(2).X(mask, :);      % E1 = sin chg + winsorizado
yh = y(mask);

configs = { 'H0_sin_nada',        'ninguno', 'ninguna'; ...
            'H1_smote_en_fold',   'smote',   'ninguna'; ...
            'H2_smote_zscore',    'smote',   'zscore' ; ...
            'H3_smote_minmax',    'smote',   'minmax' };

Honesta = table();
for c = 1:size(configs,1)
    fprintf('--- %s ---\n', configs{c,1});
    op = struct('k',5, 'semilla',42, 'modelos',{modelos}, ...
                'balanceo',configs{c,2}, 'escala',configs{c,3});
    Tc = evaluar_cv(Xh, yh, op);
    Tc.Config = repmat(configs(c,1), height(Tc), 1);
    Honesta = [Honesta; Tc];   %#ok<AGROW>
end
Honesta = movevars(Honesta, 'Config', 'Before', 'Modelo');
Honesta = removevars(Honesta, {'Recall_pos','Precision_pos','F1_pos'});
disp(Honesta);

%% --- Comparacion directa vs honesta -----------------------------------
pares = {'E2_balanceado','H1_smote_en_fold'; ...
         'E3_estandarizado','H2_smote_zscore'; ...
         'E4_normalizado','H3_smote_minmax'};
filas = {};
for p = 1:size(pares,1)
    for m = 1:numel(modelos)
        a = Res.ExactBalanceada(strcmp(Res.Etapa,pares{p,1}) & strcmp(Res.Modelo,modelos{m}));
        b = Honesta.ExactBalanceada(strcmp(Honesta.Config,pares{p,2}) & strcmp(Honesta.Modelo,modelos{m}));
        filas(end+1,:) = {pares{p,1}, pares{p,2}, modelos{m}, a, b, a-b};   %#ok<SAGROW>
    end
end
Fuga = cell2table(filas, 'VariableNames', ...
    {'Etapa_directa','Config_honesta','Modelo','ExactBal_directa','ExactBal_honesta','Diferencia'});
disp('--- Cuanto se infla la metrica al balancear antes de partir ---');
disp(Fuga);
fprintf('Inflado promedio: %.4f puntos de exactitud balanceada\n', mean(Fuga.Diferencia));

%% --- Graficos ---------------------------------------------------------
% comparativa de etapas
nombres = {E.nombre};
M = zeros(numel(nombres), numel(modelos));
for i = 1:numel(nombres)
    for m = 1:numel(modelos)
        M(i,m) = Res.ExactBalanceada(strcmp(Res.Etapa,nombres{i}) & strcmp(Res.Modelo,modelos{m}));
    end
end
f = figure('Visible','off','Position',[100 100 1000 480]);
bar(M);
set(gca,'XTickLabel', strrep(nombres,'_',' '), 'XTickLabelRotation', 20);
ylabel('exactitud balanceada (CV 5-fold)'); ylim([0 1]); grid on;
legend(modelos, 'Location','southoutside','Orientation','horizontal');
title('Ecoli - desempeno por etapa del dataset (validacion directa)');
guardar_fig(f, dir_fig, '12_modelos_por_etapa');

% directa vs honesta
f = figure('Visible','off','Position',[100 100 1000 450]);
Md = reshape(Fuga.ExactBal_directa, numel(modelos), []);
Mh = reshape(Fuga.ExactBal_honesta, numel(modelos), []);
subplot(1,2,1); bar([Md(:,1) Mh(:,1)]); ylim([0 1]); grid on;
set(gca,'XTickLabel',modelos,'XTickLabelRotation',20);
legend({'balanceado antes','balanceado dentro del fold'},'Location','southoutside');
title('E2 balanceado'); ylabel('exactitud balanceada');
subplot(1,2,2); bar([Md(:,2) Mh(:,2)]); ylim([0 1]); grid on;
set(gca,'XTickLabel',modelos,'XTickLabelRotation',20);
legend({'balanceado antes','balanceado dentro del fold'},'Location','southoutside');
title('E3 estandarizado');
sgtitle('Ecoli - efecto de balancear antes de partir en train/test');
guardar_fig(f, dir_fig, '13_fuga_por_balanceo');

% matriz de confusion del mejor modelo de la etapa E3
[~, imej] = max(Res.ExactBalanceada);
etapa_mej = Res.Etapa{imej};  mod_mej = Res.Modelo{imej};
ie = find(strcmp({E.nombre}, etapa_mej));
part = cvpartition(E(ie).y, 'KFold', 5);
yreal = {}; ypred = {};
for fo = 1:5
    itr = training(part,fo); ite = test(part,fo);
    switch mod_mej
        case 'Arbol',      mdl = fitctree(E(ie).X(itr,:), E(ie).y(itr));
        case 'KNN',        mdl = fitcknn(E(ie).X(itr,:), E(ie).y(itr), 'NumNeighbors',5);
        case 'LDA',        mdl = fitcdiscr(E(ie).X(itr,:), E(ie).y(itr), 'DiscrimType','pseudoLinear');
        case 'NaiveBayes', mdl = fitcnb(E(ie).X(itr,:), E(ie).y(itr), 'DistributionNames','kernel');
        case 'SVM',        mdl = fitcecoc(E(ie).X(itr,:), E(ie).y(itr), ...
                                 'Learners', templateSVM('KernelFunction','linear','Standardize',true));
    end
    yreal = [yreal; E(ie).y(ite)];              %#ok<AGROW>
    ypred = [ypred; cellstr(predict(mdl, E(ie).X(ite,:)))];  %#ok<AGROW>
end
f = figure('Visible','off','Position',[100 100 650 550]);
confusionchart(yreal, ypred, 'RowSummary','row-normalized');
title(sprintf('Ecoli - %s sobre %s', mod_mej, strrep(etapa_mej,'_',' ')));
guardar_fig(f, dir_fig, '14_confusion_mejor');

%% --- Exportar ---------------------------------------------------------
writetable(Res,     xls, 'Sheet', 'E4_Modelos_directa');
writetable(Honesta, xls, 'Sheet', 'E4_Modelos_honesta');
writetable(Fuga,    xls, 'Sheet', 'E4_Comparacion_fuga');
save(fullfile(base,'resultados','ecoli','ecoli_modelos.mat'), 'Res','Honesta','Fuga');
fprintf('\nPaso 4 (modelos) terminado. Mejor: %s sobre %s (exact. balanceada %.3f)\n', ...
        mod_mej, etapa_mej, Res.ExactBalanceada(imej));
