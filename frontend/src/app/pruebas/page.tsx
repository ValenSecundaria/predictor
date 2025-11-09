"use client";

import { useState, useEffect } from 'react';

interface Team {
  name: string;
  code: string;
}

interface Match {
  team_a: string;
  team_b: string;
  score_a: number;
  score_b: number;
  team_a_code: string;
  team_b_code: string;
}

const MatchList = ({ matches }: { matches: Match[] }) => {
  if (!matches.length) {
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold">Partidos</h2>
      <ul className="mt-4 space-y-4">
        {matches.map((match, index) => (
          <li key={index} className="p-4 border rounded-md">
            <p>{match.team_a} vs {match.team_b}</p>
            <p>Resultado: {match.score_a} - {match.score_b}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

const Stats = ({ matches, selectedTeam }: { matches: Match[], selectedTeam: string }) => {
  if (!matches.length) {
    return null;
  }

  const wins = matches.filter(match => {
    if (match.team_a_code === selectedTeam) {
      return match.score_a > match.score_b;
    }
    if (match.team_b_code === selectedTeam) {
      return match.score_b > match.score_a;
    }
    return false;
  }).length;

  const losses = matches.filter(match => {
    if (match.team_a_code === selectedTeam) {
      return match.score_a < match.score_b;
    }
    if (match.team_b_code === selectedTeam) {
      return match.score_b < match.score_a;
    }
    return false;
  }).length;

  const winPercentage = (wins / matches.length) * 100;
  const lossPercentage = (losses / matches.length) * 100;

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold">Estadísticas</h2>
      <p>Partidos ganados: {winPercentage.toFixed(2)}%</p>
      <p>Partidos perdidos: {lossPercentage.toFixed(2)}%</p>
    </div>
  );
};

export default function PruebasPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [matches, setMatches] = useState<Match[]>([]);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const res = await fetch('/api/v1/teams');
        const data = await res.json();
        setTeams(data);
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    };

    fetchTeams();
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      const fetchMatches = async () => {
        try {
          const res = await fetch(`/api/v1/analisis/${selectedTeam}`);
          const data = await res.json();
          setMatches(data);
        } catch (error) {
          console.error('Error fetching matches:', error);
        }
      };

      fetchMatches();
    }
  }, [selectedTeam]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Página de Pruebas</h1>

      <div className="mt-8">
        <label htmlFor="team-select" className="block text-sm font-medium text-gray-700">
          Selecciona un equipo
        </label>
        <select
          id="team-select"
          value={selectedTeam}
          onChange={(e) => setSelectedTeam(e.target.value)}
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        >
          <option value="">-- Selecciona un equipo --</option>
          {teams.map((team) => (
            <option key={team.code} value={team.code}>
              {team.name}
            </option>
          ))}
        </select>
      </div>

      <MatchList matches={matches} />
      <Stats matches={matches} selectedTeam={selectedTeam} />
    </main>
  );
}
