library ieee;
use ieee.std_logic_1164.all;

entity lfsr31 is
  port(
    clk    : in  std_logic;
    rst_n  : in  std_logic; 
    en     : in  std_logic := '1';
    load   : in  std_logic := '0';
    seed   : in  std_logic_vector(30 downto 0) := (others => '1'); -- non-zero
    q      : out std_logic_vector(30 downto 0);
    bit_o  : out std_logic
  );
end entity;

architecture rtl of lfsr31 is
  signal r : std_logic_vector(30 downto 0) := (others => '1');
begin
  q     <= r;
  bit_o <= r(0);  -- LSB seri bit

  process(clk, rst_n)
    variable feedback : std_logic;
  begin
    if rst_n = '0' then
      r <= (others => '1');  -- güvenli default
    elsif rising_edge(clk) then
      if load = '1' then
        if seed = (seed'range => '0') then
          r <= (others => '1');
        else
          r <= seed;
        end if;
      elsif en = '1' then
        -- PRBS31: x^31 + x^28 + 1  -> taps: 31,28 (0-index LSB: bit0 xor bit3)
        feedback := r(0) xor r(3);
        r <= feedback & r(30 downto 1);  -- sağa kaydır, MSB'ye feedback
      end if;
    end if;
  end process;
end architecture;
