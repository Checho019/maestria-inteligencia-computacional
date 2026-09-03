function guardar_fig(nombre)
% GUARDAR_FIG  Guarda la figura actual en informe/figuras/<nombre>.png.
% En R2025a en adelante las figuras salen con tema oscuro cuando MATLAB
% corre sin ventana, y para el informe se ven mejor en claro.
if ~exist('informe/figuras', 'dir'), mkdir('informe/figuras'); end
fig = gcf;
try
    fig.Theme = 'light';
catch
    set(fig, 'Color', 'w');
end
drawnow
exportgraphics(fig, fullfile('informe', 'figuras', [nombre '.png']), ...
               'Resolution', 150, 'BackgroundColor', 'white');
end
