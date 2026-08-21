%% =======================================================================
%  Resumen final. Cada dataset arma su propia bitacora de etapas, su tabla
%  de mejores modelos y su figura de cierre, y todo eso va a su propio libro
%  de Excel. Los dos informes se entregan por separado.
% =======================================================================
clear; clc; close all;

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));

DS = struct( ...
    'nombre', {'Ecoli', 'Bank'}, ...
    'carpeta', {'ecoli', 'bank'}, ...
    'xls', {fullfile(base,'Resultados_Ecoli.xlsx'), fullfile(base,'Resultados_Bank.xlsx')}, ...
    'balanceo', {'SMOTE', 'submuestreo'}, ...
    'etapa_sin_escalar', {'E2_balanceado', 'B2_balanceado'}, ...
    'etapa_escalada', {'E3_estandarizado', 'B3_estandarizado'});

for d = 1:numel(DS)
    fprintf('\n================ %s ================\n', DS(d).nombre);
    Mod = load(fullfile(base,'resultados',DS(d).carpeta,[DS(d).carpeta '_modelos.mat']));
    Eta = load(fullfile(base,'resultados',DS(d).carpeta,[DS(d).carpeta '_etapas.mat']));
    Et  = Eta.E;
    R   = Mod.Res;
    dir_fig = fullfile(base, 'resultados', DS(d).carpeta, 'figuras');

    %% --- Bitacora: que entra y que sale en cada paso -------------------
    % Es la tabla que conviene tener al lado al abrir cada CSV en
    % Classification Learner.
    bit = {}; conteos = {};
    for i = 1:numel(Et)
        yi = Et(i).y;
        [ci, ni] = groupcounts(yi);
        if i == 1
            dfil = 0; dvar = 0; dcla = 0; quitadas = {}; agregadas = {};
        else
            dfil = size(Et(i).X,1) - size(Et(i-1).X,1);
            dvar = numel(Et(i).vars) - numel(Et(i-1).vars);
            dcla = numel(ni) - numel(unique(Et(i-1).y));
            quitadas  = setdiff(Et(i-1).vars, Et(i).vars);
            agregadas = setdiff(Et(i).vars, Et(i-1).vars);
        end
        if isempty(quitadas),  quitadas  = {'-'}; end
        if isempty(agregadas), agregadas = {'-'}; end
        bit(end+1,:) = {Et(i).nombre, Et(i).desc, size(Et(i).X,1), dfil, ...
                        numel(Et(i).vars), dvar, numel(ni), dcla, ...
                        max(ci)/min(ci), strjoin(quitadas, ', '), ...
                        strjoin(agregadas, ', ')};                   %#ok<SAGROW>
        for c = 1:numel(ni)
            conteos(end+1,:) = {Et(i).nombre, char(ni(c)), ci(c), ...
                                100*ci(c)/numel(yi)};                %#ok<SAGROW>
        end
    end
    % 'Variables' no se puede usar como nombre de columna, choca con el
    % nombre de dimension que traen las tablas de MATLAB
    Bitacora = cell2table(bit, 'VariableNames', ...
        {'Etapa','Descripcion','Filas','Cambio_filas','N_variables', ...
         'Cambio_variables','Clases','Cambio_clases','IR', ...
         'Variables_eliminadas','Variables_agregadas'});
    Conteos = cell2table(conteos, 'VariableNames', ...
        {'Etapa','Clase','N','Porcentaje'});
    disp('--- Bitacora de cambios por etapa ---');
    disp(Bitacora(:, {'Etapa','Filas','Cambio_filas','N_variables', ...
                      'Cambio_variables','Clases','IR','Variables_eliminadas'}));

    %% --- Mejor modelo de cada etapa y aporte de cada paso --------------
    etapas = unique(R.Etapa, 'stable');
    filas = {};
    for i = 1:numel(etapas)
        sub = R(strcmp(R.Etapa, etapas{i}), :);
        [mejor, im] = max(sub.ExactBalanceada);
        filas(end+1,:) = {etapas{i}, sub.N(1), sub.Modelo{im}, mejor, ...
                          sub.Exactitud(im), sub.Kappa(im), sub.F1_macro(im)}; %#ok<SAGROW>
    end
    Resumen = cell2table(filas, 'VariableNames', ...
        {'Etapa','N','Mejor_modelo','ExactBalanceada','Exactitud','Kappa','F1_macro'});
    Resumen.Cambio_vs_etapa_previa = [NaN; diff(Resumen.ExactBalanceada)];
    disp('--- Mejor modelo de cada etapa ---'); disp(Resumen);

    %% --- Mejor etapa de cada modelo ------------------------------------
    mods = unique(R.Modelo, 'stable');
    filas = {};
    for m = 1:numel(mods)
        sub = R(strcmp(R.Modelo, mods{m}), :);
        [mejor, im] = max(sub.ExactBalanceada);
        [peor,  ip] = min(sub.ExactBalanceada);
        filas(end+1,:) = {mods{m}, mejor, sub.Etapa{im}, peor, sub.Etapa{ip}, ...
                          mejor - peor};                              %#ok<SAGROW>
    end
    PorModelo = cell2table(filas, 'VariableNames', ...
        {'Modelo','Mejor','Etapa_mejor','Peor','Etapa_peor','Sensibilidad'});
    PorModelo = sortrows(PorModelo, 'Mejor', 'descend');
    disp('--- Mejor y peor etapa de cada modelo ---'); disp(PorModelo);

    %% --- Efecto de estandarizar, modelo por modelo ---------------------
    filas = {};
    for m = 1:numel(mods)
        a = R.ExactBalanceada(strcmp(R.Etapa,DS(d).etapa_sin_escalar) & strcmp(R.Modelo,mods{m}));
        b = R.ExactBalanceada(strcmp(R.Etapa,DS(d).etapa_escalada)    & strcmp(R.Modelo,mods{m}));
        if isempty(a) || isempty(b), continue; end
        filas(end+1,:) = {mods{m}, a, b, b-a};                        %#ok<SAGROW>
    end
    Escalado = cell2table(filas, 'VariableNames', ...
        {'Modelo','Sin_escalar','Estandarizado','Ganancia'});
    disp('--- Efecto de estandarizar ---'); disp(Escalado);

    Fuga = Mod.Fuga;
    fprintf('Inflado promedio al balancear con %s antes de partir: %.4f\n', ...
            DS(d).balanceo, mean(Fuga.Diferencia));

    %% --- Figura de cierre ----------------------------------------------
    f = figure('Visible','off','Position',[100 100 1250 800]);

    subplot(2,2,1);
    bar(Resumen.ExactBalanceada, 'FaceColor',[0.35 0.6 0.75]); ylim([0 1]); grid on;
    set(gca,'XTickLabel', strrep(Resumen.Etapa,'_',' '), 'XTickLabelRotation', 25, 'FontSize', 8);
    ylabel('exactitud balanceada'); title('Mejor modelo de cada etapa');

    subplot(2,2,2);
    cam = Resumen.Cambio_vs_etapa_previa(2:end);
    b = bar(cam); b.FaceColor = 'flat';
    b.CData(cam >= 0, :) = repmat([0.4 0.7 0.5], sum(cam >= 0), 1);
    b.CData(cam <  0, :) = repmat([0.85 0.4 0.3], sum(cam <  0), 1);
    grid on; yline(0,'k-');
    set(gca,'XTickLabel', strrep(Resumen.Etapa(2:end),'_',' '), 'XTickLabelRotation', 25, 'FontSize', 8);
    ylabel('cambio respecto a la etapa anterior'); title('Cuanto aporto cada paso');

    subplot(2,2,3);
    b = barh(Escalado.Ganancia); b.FaceColor = 'flat';
    b.CData(Escalado.Ganancia >= 0, :) = repmat([0.4 0.7 0.5], sum(Escalado.Ganancia >= 0), 1);
    b.CData(Escalado.Ganancia <  0, :) = repmat([0.85 0.4 0.3], sum(Escalado.Ganancia <  0), 1);
    grid on; xline(0,'k-');
    set(gca,'YTick',1:height(Escalado),'YTickLabel',Escalado.Modelo,'FontSize',8);
    xlabel('cambio en exactitud balanceada'); title('Quien gana con estandarizar');

    subplot(2,2,4);
    mods_fuga = unique(Fuga.Modelo, 'stable');
    nm = numel(mods_fuga);
    Md = reshape(Fuga.ExactBal_directa, nm, []);
    Mh = reshape(Fuga.ExactBal_honesta, nm, []);
    bar([Md(:,1) Mh(:,1)]); ylim([0 1]); grid on;
    set(gca,'XTickLabel', mods_fuga, 'XTickLabelRotation', 20, 'FontSize', 8);
    ylabel('exactitud balanceada');
    legend({'balanceado antes de partir','balanceado dentro del pliegue'}, ...
           'Location','southoutside','FontSize',7);
    title(sprintf('Fuga al balancear con %s', DS(d).balanceo));

    sgtitle(sprintf('%s. Resumen del efecto de cada correccion sobre los modelos', DS(d).nombre));
    guardar_fig(f, dir_fig, sprintf('00_resumen_%s', lower(DS(d).nombre)));

    %% --- Exportar -------------------------------------------------------
    writetable(Bitacora,  DS(d).xls, 'Sheet', '00_Bitacora_etapas');
    writetable(Conteos,   DS(d).xls, 'Sheet', '00_Balance_por_etapa');
    writetable(Resumen,   DS(d).xls, 'Sheet', '00_Resumen_por_etapa');
    writetable(PorModelo, DS(d).xls, 'Sheet', '00_Resumen_por_modelo');
    writetable(Escalado,  DS(d).xls, 'Sheet', '00_Efecto_escalado');
end

fprintf('\nPaso 5 (resumenes) terminado. Dos libros de Excel, uno por dataset.\n');
